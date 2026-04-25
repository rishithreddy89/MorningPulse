"""MorningPulse backend entrypoint with pipeline, API, and scheduler."""

import argparse
import os
import threading
import time
from datetime import date
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

import config
from api.routes import register_routes
from utils.logger import log_step, log_info, log_error, log_success, log_data, log_request
from api.linkedin_routes import linkedin_bp
from api.chat_routes import chat_bp
from api.warroom_routes import warroom_bp
from api.export_routes import export_bp
from api.settings_routes import settings_bp
from api.scheduler_routes import scheduler_bp
from database.storage import Storage
from processor.gemini_processor import GeminiProcessor
from processor.post_selector import select_best_posts
from reporter.digest_builder import DigestBuilder
from scheduler.job_scheduler import JobScheduler
from scraper.hackernews_scraper import HackerNewsScraper
from scraper.rss_scraper import RssScraper
from scraper.news_rss_scraper import NewsRssScraper
from processor.battle_card_generator import BattleCardGenerator

app = Flask(__name__)
app.config["SECRET_KEY"] = config.FLASK_SECRET_KEY
CORS(app)

# Request logging middleware
@app.before_request
def log_request_info():
    """Log all incoming requests."""
    log_request(request.method, request.path)

MAX_GEMINI_POSTS = 40  # Send up to 40 posts to Gemini (increased from 15)
MAX_SUMMARY_LENGTH = 250  # Increased summary length
MAX_TOTAL_CHARS = 8000  # Increased total character count for Gemini input




def _empty_edtech_output() -> Dict[str, List[Dict[str, str]]]:
    """Return safe empty output when no EdTech posts are available."""
    return {
        "competitor_updates": [],
        "user_pain_points": [],
        "emerging_tech_trends": [],
    }


def _compress_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """Compress post to reduce token usage while preserving key information."""
    summary = post.get("summary", "")
    if len(summary) > MAX_SUMMARY_LENGTH:
        summary = summary[:MAX_SUMMARY_LENGTH].rsplit(" ", 1)[0] + "..."
    
    # CRITICAL: Preserve URL and source_label for source mapping
    return {
        "title": post.get("title", ""),
        "summary": summary,
        "url": post.get("url", ""),
        "source": post.get("source", ""),
        "source_label": post.get("source_label", ""),
    }


def _prepare_gemini_input(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare optimized input for Gemini with token limit safeguards."""
    # Take top N posts
    selected_posts = posts[:MAX_GEMINI_POSTS]
    
    # Compress posts (preserves URLs and source info)
    compressed_posts = [_compress_post(post) for post in selected_posts]
    
    # Ensure total size doesn't exceed limit
    combined_length = 0
    trimmed_posts = []
    
    for post in compressed_posts:
        text = post["title"] + " " + post["summary"]
        
        if combined_length + len(text) > MAX_TOTAL_CHARS:
            break
        
        combined_length += len(text)
        trimmed_posts.append(post)
    
    print(f"[Pipeline] Prepared {len(trimmed_posts)} posts for Gemini (with URLs preserved)")
    return trimmed_posts


def run_pipeline() -> Optional[Dict[str, Any]]:
    """Full pipeline: scrape, process, analyze, and save digest."""
    log_step("Pipeline starting")
    start_time = time.time()

    hn_posts: List[Dict[str, Any]] = []
    google_news_posts: List[Dict[str, Any]] = []
    reddit_posts: List[Dict[str, Any]] = []
    edsurge_posts: List[Dict[str, Any]] = []
    producthunt_posts: List[Dict[str, Any]] = []
    news_rss_posts: List[Dict[str, Any]] = []
    rss_scraper = RssScraper()

    try:
        log_step("Scraping HackerNews")
        hn_posts = HackerNewsScraper().scrape(config.TOP_HN_STORIES)
        log_data("HackerNews posts", len(hn_posts))
    except Exception as exc:
        log_error(f"HackerNews scraper failed: {exc}")

    try:
        log_step("Scraping Google News RSS")
        google_news_posts = rss_scraper.fetch_google_news()
        log_data("Google News posts", len(google_news_posts))
    except Exception as exc:
        log_error(f"Google News RSS scraper failed: {exc}")

    try:
        log_step("Scraping News RSS feeds")
        news_rss_posts = NewsRssScraper(hours_lookback=48).scrape_all()
        log_data("News RSS posts", len(news_rss_posts))
    except Exception as exc:
        log_error(f"News RSS scraper failed: {exc}")

    try:
        log_step("Scraping EdSurge")
        edsurge_posts = rss_scraper.fetch_edsurge()
        log_data("EdSurge posts", len(edsurge_posts))
    except Exception as exc:
        log_error(f"EdSurge scraper failed: {exc}")

    try:
        log_step("Scraping Product Hunt")
        producthunt_posts = rss_scraper.fetch_producthunt()
        log_data("Product Hunt posts", len(producthunt_posts))
    except Exception as exc:
        log_error(f"Product Hunt scraper failed: {exc}")

    all_posts = hn_posts + google_news_posts + news_rss_posts + edsurge_posts + producthunt_posts
    log_data("Total raw posts", len(all_posts))

    log_step("Filtering and selecting best posts")
    filtered_posts = select_best_posts(all_posts, n=40)
    log_data("Selected posts", len(filtered_posts))

    if not filtered_posts:
        log_info("No posts to process, using empty output")
        gemini_output = _empty_edtech_output()
    else:
        log_step("Preparing data for Gemini AI")
        gemini_input = _prepare_gemini_input(filtered_posts)
        log_data("Posts sent to Gemini", len(gemini_input))
        
        urls_in_input = sum(1 for p in gemini_input if p.get("url"))
        log_data("Posts with URLs", f"{urls_in_input}/{len(gemini_input)}")
        
        log_step("Sending data to Gemini AI")
        gemini_output = GeminiProcessor().process(gemini_input)
        log_success("Gemini processing complete")

    date_str = date.today().isoformat()
    log_step("Building digest")
    digest = DigestBuilder().build(gemini_output, date_str)

    log_step("Analyzing customer risk alerts")
    try:
        from processor.customer_risk_analyzer import CustomerRiskAnalyzer
        risk_analyzer = CustomerRiskAnalyzer()
        customer_risk_alerts = risk_analyzer.analyze(filtered_posts, digest)
        digest["customer_risk_alerts"] = customer_risk_alerts
        log_data("Customer risk alerts", len(customer_risk_alerts))
    except Exception as exc:
        log_error(f"Customer risk analysis failed: {exc}")
        digest["customer_risk_alerts"] = []

    competitor_updates = digest.get("competitor_updates", [])
    
    if competitor_updates:
        log_step(f"Generating battle cards for {len(competitor_updates)} competitors")
        try:
            battle_cards = BattleCardGenerator().generate_all(
                competitor_updates
            )
            digest["battle_cards"] = battle_cards
            log_data("Battle cards generated", len(battle_cards))
        except Exception as exc:
            log_error(f"Battle card generation failed: {exc}")
            digest["battle_cards"] = []
    else:
        digest["battle_cards"] = []
        log_info("No competitor updates, skipping battle cards")

    log_step("Saving digest to database")
    storage = Storage()
    storage.save_digest(digest)
    log_success("Digest saved successfully")

    elapsed = round(time.time() - start_time, 1)
    log_success(f"Pipeline complete in {elapsed}s")
    return digest


register_routes(app, run_pipeline)
app.register_blueprint(linkedin_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(warroom_bp)
app.register_blueprint(export_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(scheduler_bp)


def _resolve_frontend_dir() -> Optional[str]:
    """Locate frontend directory in common project layouts."""
    cwd_frontend = os.path.join(os.getcwd(), "frontend")
    parent_frontend = os.path.join(os.path.dirname(os.getcwd()), "frontend")

    if os.path.isdir(cwd_frontend):
        return cwd_frontend
    if os.path.isdir(parent_frontend):
        return parent_frontend
    return None


@app.route("/")
def serve_index():
    """Serve frontend index if available, otherwise show backend status."""
    frontend_dir = _resolve_frontend_dir()
    if frontend_dir:
        frontend_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(frontend_path):
            return send_file(frontend_path)
    return jsonify({"message": "MorningPulse AI Backend Running", "docs": "/api/health"})


@app.route("/<path:path>")
def serve_static(path: str):
    """Serve frontend static assets when frontend directory exists."""
    frontend_dir = _resolve_frontend_dir()
    if frontend_dir:
        full_path = os.path.join(frontend_dir, path)
        if os.path.exists(full_path):
            return send_file(full_path)
    return jsonify({"error": "Not found"}), 404


def main() -> None:
    """Parse CLI flags and run either one-off mode or scheduled server mode."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-schedule", action="store_true", help="Run pipeline once and exit")
    parser.add_argument("--run-now", action="store_true", help="Run pipeline immediately on startup")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    port = int(os.getenv("FLASK_PORT", str(args.port)))

    if args.no_schedule:
        log_info("Running single pipeline execution")
        run_pipeline()
        log_success("Pipeline execution complete")
        return

    scheduler = JobScheduler(run_pipeline)
    scheduler.start(run_now=args.run_now)

    log_success(f"Server started on port {port}")
    log_info(f"Backend running at http://localhost:{port}")
    log_info("Available endpoints:")
    log_info("  GET  /api/digest")
    log_info("  GET  /api/digest/<date>")
    log_info("  GET  /api/dates")
    log_info("  GET  /api/run")
    log_info("  GET  /api/health")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()

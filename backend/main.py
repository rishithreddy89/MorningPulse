"""MorningPulse backend entrypoint with pipeline, API, and scheduler."""

import argparse
import os
import threading
import time
from datetime import date
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, send_file
from flask_cors import CORS

import config
from api.routes import register_routes
from api.linkedin_routes import linkedin_bp
from api.chat_routes import chat_bp
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
    print("[Pipeline] Pipeline starting...")
    start_time = time.time()

    hn_posts: List[Dict[str, Any]] = []
    google_news_posts: List[Dict[str, Any]] = []
    reddit_posts: List[Dict[str, Any]] = []
    edsurge_posts: List[Dict[str, Any]] = []
    producthunt_posts: List[Dict[str, Any]] = []
    news_rss_posts: List[Dict[str, Any]] = []
    rss_scraper = RssScraper()

    try:
        hn_posts = HackerNewsScraper().scrape(config.TOP_HN_STORIES)
        print(f"[Pipeline] HackerNews: {len(hn_posts)} posts")
    except Exception as exc:
        print(f"[Pipeline] HackerNews scraper failed: {exc}")

    try:
        google_news_posts = rss_scraper.fetch_google_news()
        print(f"[Pipeline] Google News RSS: {len(google_news_posts)} posts")
    except Exception as exc:
        print(f"[Pipeline] Google News RSS scraper failed: {exc}")

    # Replace broken Reddit with new RSS sources
    try:
        news_rss_posts = NewsRssScraper(hours_lookback=48).scrape_all()
        print(f"[Pipeline] News RSS (replaces Reddit): {len(news_rss_posts)} posts")
    except Exception as exc:
        print(f"[Pipeline] News RSS scraper failed: {exc}")

    try:
        edsurge_posts = rss_scraper.fetch_edsurge()
        print(f"[Pipeline] EdSurge: {len(edsurge_posts)} posts")
    except Exception as exc:
        print(f"[Pipeline] EdSurge scraper failed: {exc}")

    try:
        producthunt_posts = rss_scraper.fetch_producthunt()
        print(f"[Pipeline] Product Hunt: {len(producthunt_posts)} posts")
    except Exception as exc:
        print(f"[Pipeline] Product Hunt scraper failed: {exc}")

    all_posts = hn_posts + google_news_posts + news_rss_posts + edsurge_posts + producthunt_posts
    print(f"[Pipeline] Total raw posts: {len(all_posts)}")

    # Use intelligent scoring and selection with diversity (20-40 posts)
    filtered_posts = select_best_posts(all_posts, n=40)

    if not filtered_posts:
        gemini_output = _empty_edtech_output()
    else:
        print("[Pipeline] Sending to Gemini...")
        # Prepare optimized input (up to 40 posts with increased token limits)
        gemini_input = _prepare_gemini_input(filtered_posts)
        print(f"[Pipeline] Gemini input: {len(gemini_input)} posts")
        
        # DEBUG: Verify URLs are preserved
        urls_in_input = sum(1 for p in gemini_input if p.get("url"))
        print(f"[Pipeline] DEBUG: {urls_in_input}/{len(gemini_input)} posts have URLs in Gemini input")
        
        # DEBUG: Show competitor distribution
        competitors_in_input = {}
        for p in gemini_input:
            comp = p.get("detected_competitor", "market_signal")
            competitors_in_input[comp] = competitors_in_input.get(comp, 0) + 1
        print(f"[Pipeline] DEBUG: Competitor distribution in Gemini input:")
        for comp, count in sorted(competitors_in_input.items(), key=lambda x: x[1], reverse=True):
            print(f"  {comp}: {count} posts")
        
        gemini_output = GeminiProcessor().process(gemini_input)

    date_str = date.today().isoformat()
    digest = DigestBuilder().build(gemini_output, date_str)

    # --- NEW STEP: BATTLE CARDS ---
    competitor_updates = digest.get("competitor_updates", [])
    
    if competitor_updates:
        print(f"[Pipeline] Generating battle cards for "
              f"{len(competitor_updates)} competitors...")
        try:
            battle_cards = BattleCardGenerator().generate_all(
                competitor_updates
            )
            digest["battle_cards"] = battle_cards
            print(f"[Pipeline] Added {len(battle_cards)} battle cards to digest")
        except Exception as exc:
            print(f"[Pipeline] Battle card generation failed: {exc}")
            digest["battle_cards"] = []
    else:
        digest["battle_cards"] = []
        print("[Pipeline] No competitor updates found, skipping battle cards")
    # --- END NEW STEP ---

    storage = Storage()
    storage.save_digest(digest)

    elapsed = round(time.time() - start_time, 1)
    print(f"[Pipeline] Pipeline complete in {elapsed}s")
    return digest


register_routes(app, run_pipeline)
app.register_blueprint(linkedin_bp)
app.register_blueprint(chat_bp)


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
        print("[Main] Running single pipeline execution...")
        run_pipeline()
        print("[Main] Done.")
        return

    scheduler = JobScheduler(run_pipeline)
    scheduler.start(run_now=args.run_now)

    print(f"[Main] Backend running at http://localhost:{port}")
    print("[Main] Available endpoints:")
    print("[Main]   GET  /api/digest")
    print("[Main]   GET  /api/digest/<date>")
    print("[Main]   GET  /api/dates")
    print("[Main]   GET  /api/run")
    print("[Main]   GET  /api/health")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()

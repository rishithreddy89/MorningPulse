"""War Room SSE streaming endpoint for real-time pipeline monitoring."""

import json
import time
from datetime import datetime
from typing import Any, Dict, Generator, List

from flask import Blueprint, Response, stream_with_context

import config
from database.storage import Storage
from processor.battle_card_generator import BattleCardGenerator
from processor.gemini_processor import GeminiProcessor
from processor.post_selector import select_best_posts
from reporter.digest_builder import DigestBuilder
from scraper.hackernews_scraper import HackerNewsScraper
from scraper.news_rss_scraper import NewsRssScraper
from scraper.rss_scraper import RssScraper

warroom_bp = Blueprint("warroom", __name__)

MAX_GEMINI_POSTS = 40
MAX_SUMMARY_LENGTH = 250
MAX_TOTAL_CHARS = 8000


def _now() -> str:
    """Return current time as HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")


def _emit(event_type: str, **kwargs) -> str:
    """Format SSE event."""
    data = {"type": event_type, "ts": _now(), **kwargs}
    return f"data: {json.dumps(data)}\n\n"


def _compress_post(post: Dict[str, Any]) -> Dict[str, Any]:
    """Compress post for Gemini."""
    summary = post.get("summary", "")
    if len(summary) > MAX_SUMMARY_LENGTH:
        summary = summary[:MAX_SUMMARY_LENGTH].rsplit(" ", 1)[0] + "..."
    return {
        "title": post.get("title", ""),
        "summary": summary,
        "url": post.get("url", ""),
        "source": post.get("source", ""),
        "source_label": post.get("source_label", ""),
    }


def _prepare_gemini_input(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare optimized Gemini input."""
    selected = posts[:MAX_GEMINI_POSTS]
    compressed = [_compress_post(p) for p in selected]
    
    combined_length = 0
    trimmed = []
    for post in compressed:
        text = post["title"] + " " + post["summary"]
        if combined_length + len(text) > MAX_TOTAL_CHARS:
            break
        combined_length += len(text)
        trimmed.append(post)
    
    return trimmed


def _is_anomaly(digest: Dict[str, Any]) -> bool:
    """Detect if today's signal count is anomalous."""
    try:
        storage = Storage()
        digests = storage.get_weekly_digests()
        if len(digests) < 3:
            return False
        
        counts = []
        for d in digests[:-1]:  # Exclude today
            total = (
                len(d.get("competitor_updates", []))
                + len(d.get("emerging_tech_trends", []))
                + len(d.get("user_pain_points", []))
            )
            counts.append(total)
        
        avg = sum(counts) / len(counts) if counts else 0
        today_count = (
            len(digest.get("competitor_updates", []))
            + len(digest.get("emerging_tech_trends", []))
            + len(digest.get("user_pain_points", []))
        )
        
        return today_count > avg * 2
    except Exception:
        return False


def _categorize_post(post: Dict[str, Any]) -> str:
    """Determine post category."""
    if post.get("detected_competitor"):
        return "competitor"
    title_lower = post.get("title", "").lower()
    if any(word in title_lower for word in ["trend", "emerging", "future", "innovation"]):
        return "trend"
    if any(word in title_lower for word in ["problem", "issue", "complaint", "frustration"]):
        return "pain_point"
    return "signal"


def _generate_warroom_stream() -> Generator[str, None, None]:
    """Generate SSE stream for war room."""
    try:
        yield _emit("start", message="Pipeline initializing...")
        time.sleep(0.5)
        
        all_posts: List[Dict[str, Any]] = []
        category_counts = {"competitor": 0, "trend": 0, "pain_point": 0, "signal": 0}
        
        # Scrape HackerNews
        yield _emit("status", message="Scraping Hacker News...", source="hackernews")
        try:
            hn_posts = HackerNewsScraper().scrape(config.TOP_HN_STORIES)
            for post in hn_posts[:5]:  # Show first 5
                category = _categorize_post(post)
                category_counts[category] += 1
                yield _emit(
                    "post",
                    source="hackernews",
                    title=post.get("title", "")[:80],
                    category=category,
                    competitor=post.get("detected_competitor", ""),
                )
                time.sleep(0.3)
            all_posts.extend(hn_posts)
            yield _emit("source_complete", source="hackernews", count=len(hn_posts))
        except Exception as e:
            yield _emit("error", message=f"HackerNews failed: {str(e)}")
        
        # Scrape Google News
        yield _emit("status", message="Scraping Google News RSS...", source="google_news")
        try:
            rss_scraper = RssScraper()
            google_posts = rss_scraper.fetch_google_news()
            for post in google_posts[:5]:
                category = _categorize_post(post)
                category_counts[category] += 1
                yield _emit(
                    "post",
                    source="google_news",
                    title=post.get("title", "")[:80],
                    category=category,
                    competitor=post.get("detected_competitor", ""),
                )
                time.sleep(0.3)
            all_posts.extend(google_posts)
            yield _emit("source_complete", source="google_news", count=len(google_posts))
        except Exception as e:
            yield _emit("error", message=f"Google News failed: {str(e)}")
        
        # Scrape News RSS
        yield _emit("status", message="Scraping EdTech News RSS...", source="news_rss")
        try:
            news_posts = NewsRssScraper(hours_lookback=48).scrape_all()
            for post in news_posts[:5]:
                category = _categorize_post(post)
                category_counts[category] += 1
                yield _emit(
                    "post",
                    source="news_rss",
                    title=post.get("title", "")[:80],
                    category=category,
                    competitor=post.get("detected_competitor", ""),
                )
                time.sleep(0.3)
            all_posts.extend(news_posts)
            yield _emit("source_complete", source="news_rss", count=len(news_posts))
        except Exception as e:
            yield _emit("error", message=f"News RSS failed: {str(e)}")
        
        # Scrape EdSurge
        yield _emit("status", message="Scraping EdSurge...", source="edsurge")
        try:
            rss_scraper = RssScraper()
            edsurge_posts = rss_scraper.fetch_edsurge()
            for post in edsurge_posts[:3]:
                category = _categorize_post(post)
                category_counts[category] += 1
                yield _emit(
                    "post",
                    source="edsurge",
                    title=post.get("title", "")[:80],
                    category=category,
                    competitor=post.get("detected_competitor", ""),
                )
                time.sleep(0.3)
            all_posts.extend(edsurge_posts)
            yield _emit("source_complete", source="edsurge", count=len(edsurge_posts))
        except Exception as e:
            yield _emit("error", message=f"EdSurge failed: {str(e)}")
        
        # Scrape Product Hunt
        yield _emit("status", message="Scraping Product Hunt...", source="producthunt")
        try:
            rss_scraper = RssScraper()
            ph_posts = rss_scraper.fetch_producthunt()
            for post in ph_posts[:3]:
                category = _categorize_post(post)
                category_counts[category] += 1
                yield _emit(
                    "post",
                    source="producthunt",
                    title=post.get("title", "")[:80],
                    category=category,
                    competitor=post.get("detected_competitor", ""),
                )
                time.sleep(0.3)
            all_posts.extend(ph_posts)
            yield _emit("source_complete", source="producthunt", count=len(ph_posts))
        except Exception as e:
            yield _emit("error", message=f"Product Hunt failed: {str(e)}")
        
        yield _emit("status", message=f"Collected {len(all_posts)} total posts")
        yield _emit("category_summary", counts=category_counts)
        time.sleep(0.5)
        
        # If no posts collected, emit done early
        if not all_posts:
            yield _emit("status", message="No posts collected. Ending pipeline.")
            yield _emit("done", message="Pipeline complete (no data).", total_signals=0)
            return
        
        # Select best posts
        yield _emit("status", message="Selecting top signals...")
        filtered_posts = select_best_posts(all_posts, n=40)
        yield _emit("status", message=f"Selected {len(filtered_posts)} posts for AI analysis")
        time.sleep(0.5)
        
        # AI Processing
        yield _emit("status", message="AI processing signals...")
        try:
            gemini_input = _prepare_gemini_input(filtered_posts)
            gemini_output = GeminiProcessor().process(gemini_input)
        except Exception as e:
            yield _emit("error", message=f"AI processing failed: {str(e)}")
            gemini_output = {"competitor_updates": [], "emerging_tech_trends": [], "user_pain_points": []}
        
        # Emit insights
        for comp in gemini_output.get("competitor_updates", [])[:5]:
            yield _emit("insight", category="competitor", text=comp.get("title", "")[:100])
            time.sleep(0.4)
        
        for trend in gemini_output.get("emerging_tech_trends", [])[:5]:
            yield _emit("insight", category="trend", text=trend.get("trend", "")[:100])
            time.sleep(0.4)
        
        for pain in gemini_output.get("user_pain_points", [])[:5]:
            yield _emit("insight", category="pain_point", text=pain.get("issue", "")[:100])
            time.sleep(0.4)
        
        # Build digest
        date_str = datetime.now().date().isoformat()
        digest = DigestBuilder().build(gemini_output, date_str)
        
        # Generate battle cards
        competitor_updates = digest.get("competitor_updates", [])
        if competitor_updates:
            yield _emit("status", message=f"Generating {len(competitor_updates)} battle cards...")
            try:
                battle_cards = BattleCardGenerator().generate_all(competitor_updates)
                digest["battle_cards"] = battle_cards
                yield _emit("status", message=f"Generated {len(battle_cards)} battle cards")
            except Exception as e:
                yield _emit("error", message=f"Battle card generation failed: {str(e)}")
                digest["battle_cards"] = []
        else:
            digest["battle_cards"] = []
        
        # Calculate pulse score
        pulse_score = min(100, len(all_posts) * 2 + len(filtered_posts))
        yield _emit("pulse", score=pulse_score)
        time.sleep(0.5)
        
        # Check for anomaly
        if _is_anomaly(digest):
            yield _emit("alert", message="Unusual signal spike — 2x above 7-day average!")
        
        # Save digest
        yield _emit("status", message="Saving digest to database...")
        try:
            Storage().save_digest(digest)
            yield _emit("done", message="Pipeline complete. Digest saved.", total_signals=len(all_posts))
        except Exception as e:
            yield _emit("error", message=f"Failed to save digest: {str(e)}")
            yield _emit("done", message="Pipeline complete (save failed).", total_signals=len(all_posts))
    
    except Exception as e:
        # Catch-all for any unexpected errors
        import traceback
        error_details = traceback.format_exc()
        print(f"[War Room] Fatal error: {error_details}")
        yield _emit("error", message=f"Fatal error: {str(e)}")
        yield _emit("done", message="Pipeline terminated due to error.", total_signals=0)


@warroom_bp.route("/api/stream/warroom")
def warroom_stream():
    """SSE endpoint for war room live feed."""
    try:
        return Response(
            stream_with_context(_generate_warroom_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[War Room] Route error: {error_details}")
        # Return error as SSE event
        def error_stream():
            yield f"data: {{\"type\":\"error\",\"message\":\"Failed to start stream: {str(e)}\",\"ts\":\"{_now()}\"}}\n\n"
            yield f"data: {{\"type\":\"done\",\"message\":\"Stream terminated\",\"ts\":\"{_now()}\"}}\n\n"
        return Response(
            stream_with_context(error_stream()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
            },
        )


@warroom_bp.route("/api/run-now", methods=["POST"])
def run_now():
    """Trigger for demo — client should immediately connect to SSE."""
    return {"status": "ready", "message": "Connect to /api/stream/warroom"}


@warroom_bp.route("/api/warroom/health")
def warroom_health():
    """Health check for war room endpoint."""
    return {
        "status": "ok",
        "message": "War Room endpoint is available",
        "timestamp": _now(),
    }

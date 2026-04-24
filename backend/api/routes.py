"""Flask route registration for MorningPulse backend APIs."""

import threading
from datetime import datetime
from typing import Callable

from flask import Flask, jsonify, request

from database.storage import Storage
from processor.gemini_processor import GeminiProcessor


def register_routes(app: Flask, run_pipeline_fn: Callable[[], object]) -> None:
    """Register all API routes on the Flask app instance."""

    @app.get("/api/digest")
    def get_latest_digest():
        """Return latest digest."""
        _ = request.args
        digest = Storage().get_today_digest()
        if not digest:
            return (
                jsonify(
                    {
                        "error": "No digest available. Click Refresh to generate one.",
                        "status": "empty",
                    }
                ),
                404,
            )
        return jsonify(digest)

    @app.get("/api/digest/<date_str>")
    def get_digest_by_date(date_str: str):
        """Return digest for specific date (YYYY-MM-DD)."""
        digest = Storage().get_digest(date_str)
        if not digest:
            return jsonify({"error": f"No digest for {date_str}"}), 404
        return jsonify(digest)

    @app.get("/api/dates")
    def get_dates():
        """Return all available digest dates."""
        dates = Storage().get_all_dates()
        return jsonify({"dates": dates})

    @app.get("/api/run")
    def run_pipeline():
        """Trigger pipeline in background thread."""

        def run_in_bg() -> None:
            """Execute the pipeline safely in a daemon thread."""
            try:
                run_pipeline_fn()
            except Exception as exc:
                print(f"[API] Pipeline error: {exc}")

        thread = threading.Thread(target=run_in_bg, daemon=True)
        thread.start()

        return jsonify(
            {
                "status": "running",
                "message": "Pipeline started. Refresh in 60-90 seconds.",
            }
        )

    @app.get("/api/weekly-memo")
    def get_weekly_memo():
        """Generate and return weekly strategy memo."""
        digests = Storage().get_weekly_digests()
        if len(digests) < 2:
            return jsonify({"error": "Need at least 2 days of data"}), 400
        memo = GeminiProcessor().generate_weekly_memo(digests)
        return jsonify(
            {
                "memo": memo,
                "generated_at": datetime.now().isoformat(),
                "days_analyzed": len(digests),
            }
        )

    @app.get("/api/sentiment")
    def get_sentiment():
        """Return sentiment data from latest digest."""
        digest = Storage().get_today_digest()
        if not digest:
            return jsonify({"error": "No digest available"}), 404
        return jsonify(
            {
                "sentiment": digest.get("sentiment_analysis", {}),
                "market_sentiment": digest.get("market_sentiment", {}),
            }
        )

    @app.get("/api/trend-velocity")
    def get_trend_velocity():
        """Return trend velocity data."""
        digest = Storage().get_today_digest()
        if not digest:
            return jsonify({"error": "No digest available"}), 404
        return jsonify(
            {
                "velocity": digest.get("trend_velocity", []),
                "trending_keywords": digest.get("trending_keywords", {}),
            }
        )

    @app.get("/api/sources")
    def get_sources():
        """Return source metadata."""
        digest = Storage().get_today_digest()
        if not digest:
            return jsonify({"error": "No digest available"}), 404
        return jsonify(
            {
                "sources": digest.get("meta", {}).get("sources", {}),
                "total": digest.get("meta", {}).get("total_posts_analyzed", 0),
            }
        )

    @app.get("/api/health")
    def get_health():
        """Health check endpoint."""
        digest = Storage().get_today_digest()
        return jsonify(
            {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "last_digest": digest.get("date") if digest else None,
                "has_today_digest": digest is not None,
            }
        )

    @app.get("/api/battle-cards")
    def get_battle_cards():
        """Return battle cards from the latest digest."""
        try:
            from database.storage import Storage
            storage = Storage()
            digest = storage.get_today_digest()
            
            if not digest:
                return jsonify({
                    "battle_cards": [],
                    "message": "No digest available yet"
                }), 404
            
            battle_cards = digest.get("battle_cards", [])
            digest_date = digest.get("date", "")
            
            return jsonify({
                "date": digest_date,
                "battle_cards": battle_cards,
                "total": len(battle_cards)
            })
        
        except Exception as e:
            print(f"Battle cards endpoint error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.get("/api/battle-cards/<date_str>")
    def get_battle_cards_by_date(date_str: str):
        """Return battle cards for a specific date."""
        try:
            from database.storage import Storage
            storage = Storage()
            digest = storage.get_digest(date_str)
            
            if not digest:
                return jsonify({"error": f"No digest for {date_str}"}), 404
            
            return jsonify({
                "date": date_str,
                "battle_cards": digest.get("battle_cards", []),
                "total": len(digest.get("battle_cards", []))
            })
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

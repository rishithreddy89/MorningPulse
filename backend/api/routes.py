"""Flask route registration for MorningPulse backend APIs."""

import threading
from datetime import datetime
from typing import Callable

from flask import Flask, jsonify, request

from database.storage import Storage
from processor.gemini_processor import GeminiProcessor
from utils.logger import log_info, log_error, log_step, log_success


def register_routes(app: Flask, run_pipeline_fn: Callable[[], object]) -> None:
    """Register all API routes on the Flask app instance."""

    @app.get("/api/digest")
    def get_latest_digest():
        """Return latest digest."""
        _ = request.args
        log_info("Fetching latest digest")
        digest = Storage().get_today_digest()
        if not digest:
            log_error("No digest available")
            return (
                jsonify(
                    {
                        "error": "No digest available. Click Refresh to generate one.",
                        "status": "empty",
                    }
                ),
                404,
            )
        log_success("Latest digest retrieved")
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
        log_step("Pipeline triggered via API")

        def run_in_bg() -> None:
            """Execute the pipeline safely in a daemon thread."""
            try:
                run_pipeline_fn()
            except Exception as exc:
                log_error(f"Pipeline error: {exc}")

        thread = threading.Thread(target=run_in_bg, daemon=True)
        thread.start()
        log_info("Pipeline started in background")

        return jsonify(
            {
                "status": "running",
                "message": "Pipeline started. Refresh in 60-90 seconds.",
            }
        )

    @app.get("/api/weekly-memo")
    def get_weekly_memo():
        """Generate and return weekly strategy memo."""
        log_step("Generating weekly memo")
        digests = Storage().get_weekly_digests()
        if len(digests) < 2:
            log_error("Not enough data for weekly memo")
            return jsonify({"error": "Need at least 2 days of data"}), 400
        memo = GeminiProcessor().generate_weekly_memo(digests)
        log_success("Weekly memo generated")
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

    @app.post("/api/solutions")
    def get_solutions():
        """Generate AI-powered solutions for a user pain point."""
        try:
            import json
            from processor.gemini_processor import GeminiProcessor
            
            body = request.get_json()
            pain_point = body.get("pain_point", "")
            description = body.get("description", "")
            source = body.get("source", "")

            if not pain_point:
                log_error("No pain point provided")
                return jsonify({"error": "No pain point provided"}), 400

            log_step(f"Generating solutions for: {pain_point[:50]}...")

            prompt = f"""You are a senior product strategist for Campus Cortex AI, an EdTech SaaS platform serving K-12 schools and districts in India.

A real user pain point has been detected from {source}:

PAIN POINT: {pain_point}
DESCRIPTION: {description}

Generate exactly 4 actionable product solutions that Campus Cortex AI can design, build, or position to directly solve this pain point.

For each solution return:
- title: short feature name (max 6 words)
- what: one sentence describing what it is
- how: one sentence describing how Campus Cortex builds it
- impact: one sentence on the business/user impact
- effort: "low" | "medium" | "high" (engineering effort to build)
- priority: "quick win" | "core feature" | "bold move"
- target_user: "admin" | "teacher" | "student" | "district"

Respond ONLY with a valid JSON array. No markdown. No explanation. No preamble. No backticks. Start directly with [ and end with ].

Example format:
[
  {{
    "title": "Tool usage audit dashboard",
    "what": "Shows admins which tools are actively used vs idle.",
    "how": "Pull login frequency data via API integrations or CSV upload.",
    "impact": "Admins cut unused tools saving $10k+ per district annually.",
    "effort": "low",
    "priority": "quick win",
    "target_user": "admin"
  }}
]
"""

            # Call Gemini
            processor = GeminiProcessor()
            log_info("Sending request to Gemini AI")
            response = processor.model.generate_content(prompt)
            raw = response.text.strip()

            # Strip any accidental markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            solutions = json.loads(raw)
            log_success(f"Generated {len(solutions)} solutions")

            return jsonify({
                "pain_point": pain_point,
                "solutions": solutions,
                "source": source
            })

        except json.JSONDecodeError as e:
            log_error(f"JSON decode error: {e}")
            return jsonify({
                "error": f"AI returned invalid JSON: {e}",
                "solutions": []
            }), 500
        except Exception as e:
            log_error(f"Solutions API error: {e}")
            return jsonify({"error": str(e), "solutions": []}), 500

    @app.get("/api/customer-risk")
    def get_customer_risk():
        """Get customer risk alerts from latest digest."""
        try:
            from database.storage import Storage
            
            log_info("Fetching customer risk alerts")
            storage = Storage()
            digest = storage.get_today_digest()
            
            if not digest:
                log_error("No digest available for risk alerts")
                return jsonify({
                    "alerts": [],
                    "message": "No digest available yet"
                }), 404
            
            alerts = digest.get("customer_risk_alerts", [])
            log_success(f"Retrieved {len(alerts)} risk alerts")
            
            return jsonify({
                "date": digest.get("date", ""),
                "alerts": alerts,
                "total": len(alerts)
            })
        
        except Exception as e:
            log_error(f"Customer risk API error: {e}")
            return jsonify({"error": str(e)}), 500

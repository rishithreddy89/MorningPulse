"""Settings management routes for MorningPulse configuration."""

import json
import os
from datetime import datetime

from flask import Blueprint, jsonify, request

settings_bp = Blueprint("settings", __name__, url_prefix="/api")

CONFIG_FILE = "config.json"


def load_settings():
    """Load settings from config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Settings] Error loading config: {e}")
    
    # Return defaults
    return {
        "organization": "MorningPulse AI",
        "email": "",
        "delivery_time": "08:00",
        "email_enabled": True,
        "include_competitors": True,
        "include_low_priority": False,
    }


def save_settings(data):
    """Save settings to config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"[Settings] Error saving config: {e}")
        return False


@settings_bp.route("/settings", methods=["GET"])
def get_settings():
    """Get current settings."""
    try:
        settings = load_settings()
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/settings", methods=["POST"])
def save_settings_route():
    """Save settings and reschedule email job."""
    try:
        data = request.get_json()

        # Validate delivery_time format HH:MM
        delivery_time = data.get("delivery_time", "08:00")
        try:
            datetime.strptime(delivery_time, "%H:%M")
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM"}), 400

        # Save settings
        if not save_settings(data):
            return jsonify({"error": "Failed to save settings"}), 500

        # Reschedule email job with new time
        from scheduler.email_scheduler import reschedule_email_job, email_scheduler
        reschedule_email_job(delivery_time)
        
        # Get confirmation that job was scheduled
        job = email_scheduler.get_job("daily_full_pipeline")
        if job:
            next_run = "Job scheduled successfully"
        else:
            next_run = "unknown"

        return jsonify({
            "success": True,
            "message": f"Settings saved. Full pipeline + email scheduled at {delivery_time} IST daily.",
            "delivery_time": delivery_time,
            "next_run": next_run,
        })

    except Exception as e:
        print(f"[Settings] Save error: {e}")
        return jsonify({"error": str(e)}), 500


@settings_bp.route("/settings/test-pipeline", methods=["POST"])
def test_pipeline():
    """Trigger full pipeline manually for testing."""
    import threading
    from scheduler.email_scheduler import run_full_pipeline_and_email
    
    t = threading.Thread(target=run_full_pipeline_and_email)
    t.daemon = True
    t.start()
    
    return jsonify({
        "status": "Pipeline started in background. Check Flask terminal for logs."
    })

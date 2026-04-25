"""Scheduler status routes for debugging."""

from flask import Blueprint, jsonify

from scheduler.email_scheduler import get_scheduler_status

scheduler_bp = Blueprint("scheduler", __name__, url_prefix="/api/scheduler")


@scheduler_bp.route("/status")
def status():
    """Get status of all scheduled jobs."""
    try:
        status_data = get_scheduler_status()
        return jsonify(status_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

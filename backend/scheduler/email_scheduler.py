"""Email scheduler for automated daily brief delivery."""

import os
import traceback
from datetime import datetime

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# IST timezone
IST = pytz.timezone('Asia/Calcutta')

# Global scheduler instance with IST timezone
email_scheduler = BackgroundScheduler(timezone=IST)

# Flask app reference (set during init)
_flask_app = None


def set_flask_app(app):
    """Store Flask app reference for context."""
    global _flask_app
    _flask_app = app


def run_full_pipeline_and_email():
    """Full pipeline: scrape → AI → save → email. Runs at CEO's scheduled time."""
    from api.settings_routes import load_settings
    from database.storage import Storage
    from reporter.email_reporter import EmailReporter
    
    date_str = datetime.now(IST).strftime('%Y-%m-%d')
    time_str = datetime.now(IST).strftime('%H:%M:%S')
    print(f"[Pipeline] Starting full pipeline for {date_str} at {time_str} IST")
    
    try:
        settings = load_settings()
        
        if not settings.get("email_enabled", True):
            print("[Pipeline] Email delivery disabled. Aborting.")
            return
        
        email = settings.get("email", "")
        if not email:
            print("[Pipeline] No email configured. Aborting.")
            return
        
        # Import pipeline function
        from main import run_pipeline
        
        # STEP 1: Run full pipeline and save
        print("[Pipeline] Running scrape + AI processing...")
        digest = run_pipeline()
        
        if not digest:
            print("[Pipeline] Pipeline returned no digest. Sending error alert.")
            _send_error_email("Pipeline produced no digest today.")
            return
        
        # STEP 2: Verify digest was saved and has content
        storage = Storage()
        saved_digest = storage.get_today_digest()
        
        if not saved_digest:
            print("[Pipeline] Digest save appeared to succeed but reloading returned None.")
            _send_error_email("Digest save verification failed.")
            return
        
        # Verify content exists
        content_sections = [
            saved_digest.get("executive_summary", ""),
            saved_digest.get("high_priority_alerts", []),
            saved_digest.get("competitor_updates", []),
            saved_digest.get("user_pain_points", []),
            saved_digest.get("emerging_tech_trends", [])
        ]
        
        has_content = any([
            len(s) > 0 if isinstance(s, (list, str)) else False
            for s in content_sections
        ])
        
        if not has_content:
            print("[Pipeline] Saved digest has no content. Gemini processing may have failed.")
            _send_error_email("Digest has no content — Gemini processing failed.")
            return
        
        # STEP 3: Send email with PDF (only after verified save)
        print("[Pipeline] Digest verified. Generating PDF and sending email...")
        reporter = EmailReporter()
        success = reporter.send(saved_digest)
        
        if success:
            print(f"[Pipeline] Complete. Email sent to {email} at {datetime.now(IST).strftime('%H:%M')} IST")
        else:
            print(f"[Pipeline] Email send failed for {email}")
            _send_error_email("Pipeline ran but email delivery failed.")
    
    except Exception as e:
        print(f"[Pipeline] Error: {e}")
        traceback.print_exc()
        _send_error_email(f"Pipeline error: {e}")


def _send_error_email(reason: str):
    """Send plain-text alert if pipeline fails."""
    try:
        from api.settings_routes import load_settings
        import smtplib
        from email.mime.text import MIMEText
        
        settings = load_settings()
        recipient = settings.get("email", "")
        if not recipient:
            return
        
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        if not smtp_user or not smtp_pass:
            return
        
        msg = MIMEText(
            f"MorningPulse AI pipeline issue on {datetime.now(IST).strftime('%Y-%m-%d')}:\n\n"
            f"{reason}\n\nCheck Flask logs for details."
        )
        msg["From"] = f"MorningPulse AI <{smtp_user}>"
        msg["To"] = recipient
        msg["Subject"] = f"MorningPulse Alert — {datetime.now(IST).strftime('%Y-%m-%d')}"
        
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.send_message(msg)
    except:
        pass


def reschedule_email_job(delivery_time: str):
    """
    Reschedule full pipeline + email job with new delivery time in IST.
    Called when CEO saves settings.
    """
    try:
        hour, minute = map(int, delivery_time.split(":"))

        if email_scheduler.get_job("daily_full_pipeline"):
            email_scheduler.remove_job("daily_full_pipeline")
            print(f"[EmailScheduler] Removed old job")

        email_scheduler.add_job(
            func=run_full_pipeline_and_email,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=IST),
            id="daily_full_pipeline",
            name=f"Full pipeline + email at {delivery_time} IST",
            replace_existing=True,
            misfire_grace_time=600,
        )
        print(f"[EmailScheduler] Full pipeline scheduled for {delivery_time} IST daily")
        return True

    except Exception as e:
        print(f"[EmailScheduler] Reschedule error: {e}")
        return False


def init_email_scheduler(app):
    """Initialize email scheduler on app startup."""
    try:
        # Store Flask app reference
        set_flask_app(app)
        
        from api.settings_routes import load_settings

        settings = load_settings()
        delivery_time = settings.get("delivery_time", "08:00")

        reschedule_email_job(delivery_time)

        if not email_scheduler.running:
            email_scheduler.start()
            print(f"[EmailScheduler] Started. Full pipeline scheduled at {delivery_time} IST daily.")
        
        # Verify job registered
        job = email_scheduler.get_job("daily_full_pipeline")
        if job:
            # Get next run time from scheduler directly
            next_run = email_scheduler.get_job("daily_full_pipeline")
            if next_run:
                print(f"[EmailScheduler] Job registered successfully")
            else:
                print("[EmailScheduler] Job registered but next run time unavailable")
        else:
            print("[EmailScheduler] WARNING: Job not found after registration!")

    except Exception as e:
        print(f"[EmailScheduler] Init error: {e}")
        traceback.print_exc()


def get_scheduler_status():
    """Get status of all scheduled jobs."""
    jobs = []
    for job in email_scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if hasattr(job, 'next_run_time') and job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return {"jobs": jobs, "running": email_scheduler.running}

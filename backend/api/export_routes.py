"""PDF export and email routes for MorningPulse reports."""

import io
import os
import smtplib
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, jsonify, make_response, render_template, request

from database.storage import Storage

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


def _get_today() -> str:
    """Return today's date in ISO format."""
    from datetime import date
    return date.today().isoformat()


def _load_digest(date_str: str):
    """Load digest for given date from storage."""
    storage = Storage()
    digest = storage.get_digest(date_str)
    if not digest:
        # Try today's digest if specific date not found
        if date_str == _get_today():
            digest = storage.get_today_digest()
    return digest


def _generate_pdf_bytes(digest, date_str: str, org_name: str) -> bytes:
    """Generate PDF bytes from digest data."""
    html = render_template(
        "pdf_report.html",
        digest=digest,
        date=date_str,
        org_name=org_name,
        generated_at=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
    )

    # Try weasyprint first
    try:
        from weasyprint import HTML
        print("[Export] Using weasyprint for PDF generation")
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except ImportError as e:
        print(f"[Export] weasyprint not available: {e}")
        # Try xhtml2pdf fallback
        try:
            from xhtml2pdf import pisa
            print("[Export] Using xhtml2pdf fallback for PDF generation")
            pdf_buffer = io.BytesIO()
            pisa.CreatePDF(html, dest=pdf_buffer)
            return pdf_buffer.getvalue()
        except ImportError as e2:
            print(f"[Export] xhtml2pdf not available: {e2}")
            raise ImportError(
                "No PDF library available. Install one of: pip install weasyprint OR pip install xhtml2pdf"
            ) from e2
    except Exception as e:
        print(f"[Export] PDF generation error: {e}")
        raise


@export_bp.route("/pdf")
def export_pdf():
    """Generate and download PDF report for a given date."""
    try:
        date_str = request.args.get("date", _get_today())
        digest = _load_digest(date_str)

        if not digest:
            return jsonify({"error": f"No digest found for {date_str}"}), 404

        # Default org name
        org_name = "MorningPulse AI"

        # Generate PDF
        pdf_bytes = _generate_pdf_bytes(digest, date_str, org_name)

        # Return as downloadable file
        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = (
            f"attachment; filename=morningpulse-{date_str}.pdf"
        )
        return response

    except Exception as e:
        print(f"[Export] PDF generation error: {e}")
        return jsonify({"error": str(e)}), 500


@export_bp.route("/email", methods=["POST"])
def email_pdf():
    """Send PDF report via email."""
    try:
        body = request.get_json()
        recipient = body.get("email")
        date_str = body.get("date", _get_today())
        settings = body.get("settings", {})

        if not recipient:
            return jsonify({"error": "No email address provided"}), 400

        # Load SMTP config from environment
        smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")

        if not smtp_user or not smtp_pass:
            return jsonify({
                "error": "Email not configured. Set SMTP_USER and SMTP_PASS environment variables."
            }), 500

        # Load digest
        digest = _load_digest(date_str)
        if not digest:
            return jsonify({"error": f"No digest found for {date_str}"}), 404

        # Generate PDF
        org_name = settings.get("organization", "MorningPulse AI")
        pdf_bytes = _generate_pdf_bytes(digest, date_str, org_name)

        # Build email
        msg = MIMEMultipart()
        msg["From"] = f"MorningPulse AI <{smtp_user}>"
        msg["To"] = recipient
        msg["Subject"] = f"MorningPulse Brief — {date_str}"

        # Email body
        summary = digest.get("summary", "")
        if not summary and digest.get("emerging_tech_trends"):
            summary = f"{len(digest['emerging_tech_trends'])} emerging trends detected"
        
        body_text = f"""Good morning,

Your MorningPulse AI market intelligence brief for {date_str} is attached.

Summary: {summary[:200]}{"..." if len(summary) > 200 else ""}

View full dashboard: http://localhost:8080

— MorningPulse AI
"""
        msg.attach(MIMEText(body_text, "plain"))

        # Attach PDF
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_part.add_header(
            "Content-Disposition", "attachment", filename=f"morningpulse-{date_str}.pdf"
        )
        msg.attach(pdf_part)

        # Send via SMTP
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return jsonify({"success": True, "message": f"Report sent to {recipient}"})

    except Exception as e:
        print(f"[Export] Email error: {e}")
        return jsonify({"error": str(e)}), 500

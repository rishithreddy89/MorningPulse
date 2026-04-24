"""Flask routes for LinkedIn intelligence feature."""

import json
import os
import threading
from datetime import date

from flask import Blueprint, jsonify
from supabase import create_client

from scraper.linkedin_scraper import LinkedInScraper
from processor.linkedin_analyzer import LinkedInAnalyzer


linkedin_bp = Blueprint("linkedin", __name__, url_prefix="/api/linkedin")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def _save_linkedin_data(data: dict) -> bool:
    """Save LinkedIn data to Supabase or local fallback.
    
    Returns True if saved to Supabase, False if using local fallback.
    """
    print("Saving LinkedIn data...")
    
    try:
        supabase.table("linkedin_intel").upsert({
            "date": date.today().isoformat(),
            "content": json.dumps(data)
        }).execute()
        
        print("✅ Saved to Supabase")
        return True
    
    except Exception as e:
        print(f"⚠️  Supabase error: {e}")
        print("Falling back to local storage...")
        
        try:
            os.makedirs("outputs", exist_ok=True)
            file_path = f"outputs/linkedin_{date.today().isoformat()}.json"
            
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Saved locally to {file_path}")
            return False
        
        except Exception as local_err:
            print(f"❌ Local storage error: {local_err}")
            return False


def _load_latest_intel() -> dict:
    """Load latest LinkedIn intelligence from Supabase or local files."""
    
    # Try Supabase first
    try:
        result = (supabase
            .table("linkedin_intel")
            .select("content, date")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        
        if result.data:
            content = result.data[0]["content"]
            if isinstance(content, str):
                content = json.loads(content)
            return content
    
    except Exception as e:
        print(f"Supabase query error: {e}")
    
    # Fallback to local files
    try:
        file_path = f"outputs/linkedin_{date.today().isoformat()}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    
    except Exception as e:
        print(f"Local file error: {e}")
    
    # Return empty result
    return {
        "error": "No LinkedIn data available. Click Scrape LinkedIn.",
        "competitor_activities": [],
        "market_signals": [],
        "summary": "",
        "raw_posts": []
    }


@linkedin_bp.route("/scrape", methods=["GET"])
def scrape_linkedin():
    """Trigger LinkedIn scrape + analysis in background thread."""
    
    def run_linkedin_pipeline():
        try:
            print("LinkedIn pipeline starting...")
            
            scraper = LinkedInScraper(headless=True)
            posts = scraper.scrape_all()
            
            if not posts:
                print("LinkedIn: no posts collected")
                return
            
            analysis = LinkedInAnalyzer().analyze(posts)
            
            analysis["raw_posts"] = posts
            analysis["total_posts"] = len(posts)
            analysis["date"] = date.today().isoformat()
            
            # Save with fallback to local storage
            _save_linkedin_data(analysis)
            
            print(f"LinkedIn pipeline complete. {len(posts)} posts analyzed.")
        
        except Exception as e:
            print(f"LinkedIn pipeline error: {e}")
    
    thread = threading.Thread(target=run_linkedin_pipeline, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "running",
        "message": "LinkedIn scrape started. Check back in 3-5 minutes."
    })


@linkedin_bp.route("/intel", methods=["GET"])
def get_latest_intel():
    """Return latest LinkedIn intelligence."""
    try:
        data = _load_latest_intel()
        return jsonify(data)
    
    except Exception as e:
        print(f"Error loading intel: {e}")
        return jsonify({
            "error": "Error loading data",
            "competitor_activities": [],
            "market_signals": [],
            "summary": "",
            "raw_posts": []
        }), 200


@linkedin_bp.route("/intel/<date_str>", methods=["GET"])
def get_intel_by_date(date_str):
    """Return LinkedIn intelligence for specific date."""
    try:
        # Try Supabase first
        try:
            result = (supabase
                .table("linkedin_intel")
                .select("content, date")
                .eq("date", date_str)
                .limit(1)
                .execute()
            )
            
            if result.data:
                content = result.data[0]["content"]
                if isinstance(content, str):
                    content = json.loads(content)
                return jsonify(content)
        
        except Exception as e:
            print(f"Supabase query error: {e}")
        
        # Fallback to local file
        file_path = f"outputs/linkedin_{date_str}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return jsonify(json.load(f))
        
        return jsonify({"error": f"No data for {date_str}"}), 200
    
    except Exception as e:
        print(f"Error loading date intel: {e}")
        return jsonify({"error": str(e)}), 200


@linkedin_bp.route("/status", methods=["GET"])
def check_status():
    """Check if LinkedIn scrape data exists for today."""
    try:
        # Try Supabase first
        try:
            result = (supabase
                .table("linkedin_intel")
                .select("date, created_at")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if result.data:
                return jsonify({
                    "status": "complete",
                    "has_data": True,
                    "last_scraped": result.data[0]["date"],
                    "created_at": result.data[0].get("created_at", ""),
                    "source": "supabase"
                }), 200
        
        except Exception as e:
            print(f"Supabase status error: {e}")
        
        # Fallback to local file
        file_path = f"outputs/linkedin_{date.today().isoformat()}.json"
        if os.path.exists(file_path):
            return jsonify({
                "status": "complete",
                "has_data": True,
                "last_scraped": date.today().isoformat(),
                "source": "local"
            }), 200
        
        # No data found
        return jsonify({
            "status": "no_data",
            "has_data": False,
            "last_scraped": None,
            "message": "No LinkedIn data available"
        }), 200
    
    except Exception as e:
        print(f"Status check error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 200

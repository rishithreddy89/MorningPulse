"""Chat API endpoint for asking questions about digest data."""

import json
import os
from datetime import date

from flask import Blueprint, jsonify, request
from supabase import create_client
import google.generativeai as genai

chat_bp = Blueprint("chat", __name__, url_prefix="/api")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def _load_digest_for_date(date_str: str) -> dict:
    """Load digest data from Supabase or local fallback."""
    
    # Try Supabase first
    try:
        result = (supabase
            .table("digests")
            .select("*")
            .eq("date", date_str)
            .limit(1)
            .execute()
        )
        
        if result.data:
            digest = result.data[0]
            # Parse content if it's a string
            if isinstance(digest.get("content"), str):
                digest["content"] = json.loads(digest["content"])
            return digest
    
    except Exception as e:
        print(f"Supabase digest query error: {e}")
    
    # Try LinkedIn intel table
    try:
        result = (supabase
            .table("linkedin_intel")
            .select("*")
            .eq("date", date_str)
            .limit(1)
            .execute()
        )
        
        if result.data:
            intel = result.data[0]
            if isinstance(intel.get("content"), str):
                intel["content"] = json.loads(intel["content"])
            return {"linkedin_intel": intel}
    
    except Exception as e:
        print(f"Supabase LinkedIn query error: {e}")
    
    # Fallback to local files
    try:
        file_path = f"outputs/digest_{date_str}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Local digest file error: {e}")
    
    try:
        file_path = f"outputs/linkedin_{date_str}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return {"linkedin_intel": json.load(f)}
    except Exception as e:
        print(f"Local LinkedIn file error: {e}")
    
    return None


def _extract_sources_from_digest(digest: dict) -> list:
    """Extract unique sources from digest data."""
    sources = set()
    
    # From main digest
    if "content" in digest:
        content = digest["content"]
        
        # Competitor updates
        for update in content.get("competitor_updates", []):
            for source in update.get("sources", []):
                sources.add(source.get("source_name", "Unknown"))
        
        # User pain points
        for pain in content.get("user_pain_points", []):
            for source in pain.get("sources", []):
                sources.add(source.get("source_name", "Unknown"))
        
        # Tech trends
        for trend in content.get("emerging_tech_trends", []):
            for source in trend.get("sources", []):
                sources.add(source.get("source_name", "Unknown"))
    
    # From LinkedIn intel
    if "linkedin_intel" in digest:
        intel = digest["linkedin_intel"]
        if isinstance(intel, dict) and "content" in intel:
            content = intel["content"]
            for activity in content.get("competitor_activities", []):
                company = activity.get("competitor_name", "Unknown")
                sources.add(f"LinkedIn - {company}")
    
    return list(sources)


@chat_bp.route("/chat", methods=["POST", "OPTIONS"])
def chat_with_digest():
    """Chat endpoint for asking questions about digest data."""
    
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({}), 200
    
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({
                "answer": "Invalid request. Please provide a message.",
                "sources": []
            }), 200
        
        user_message = data.get("message", "").strip()
        date_str = data.get("date", date.today().isoformat())
        
        if not user_message:
            return jsonify({
                "answer": "Please provide a question.",
                "sources": []
            }), 200
        
        print(f"Chat request: '{user_message}' for date {date_str}")
        
        # Load digest data
        digest = _load_digest_for_date(date_str)
        
        if not digest:
            return jsonify({
                "answer": f"No digest found for {date_str}. Try running the pipeline first.",
                "sources": []
            }), 200
        
        # Extract sources
        sources = _extract_sources_from_digest(digest)
        
        # Build system prompt with digest data
        digest_json = json.dumps(digest, indent=2)[:10000]  # Limit size
        
        system_prompt = f"""You are a market intelligence analyst for MorningPulse AI.
Answer the user's question using ONLY the data below.
If the answer is not in the data, say "I don't have enough data on that today."
Never hallucinate. Always cite which company or source your answer comes from.
Keep responses concise - maximum 3 short paragraphs.

TODAY'S DIGEST DATA:
{digest_json}
"""
        
        # Call Gemini
        try:
            response = model.generate_content([
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I understand. I will answer questions using only the digest data provided."]},
                {"role": "user", "parts": [user_message]}
            ])
            
            answer = response.text.strip()
            
            print(f"Chat response generated: {len(answer)} chars")
            
            return jsonify({
                "answer": answer,
                "sources": sources[:10]  # Limit to 10 sources
            }), 200
        
        except Exception as e:
            import traceback
            print(f"Gemini error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                "answer": f"Error processing question: {str(e)}",
                "sources": []
            }), 200
    
    except Exception as e:
        import traceback
        print(f"Chat endpoint error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "answer": f"An error occurred: {str(e)}",
            "sources": []
        }), 200

"""Battle card generator for competitive intelligence."""

import json
import os
import re
import time
from typing import Any, Dict, List, Optional

import google.generativeai as genai


BATTLE_CARD_PROMPT = """
CRITICAL: Respond with ONLY a JSON object. Start with {{ 
end with }}. No text before or after. No markdown.

You are a competitive intelligence analyst for Campus Cortex 
AI, an EdTech SaaS startup that helps schools manage 
operations, communications, and teacher workflows.

Campus Cortex AI strengths (for context):
- Real-time parent-teacher communication tools
- AI-powered gradebook with auto-insights  
- Unified school operations dashboard
- Affordable pricing for small/mid-size schools
- Easy onboarding (under 2 hours setup)

Generate a competitive battle card for this EdTech competitor:

Competitor: {competitor_name}
What they did: {competitor_update}
Impact level: {impact_level}
Source context: {source_context}

Return this exact JSON:
{{
  "competitor_name": "{competitor_name}",
  "their_strength": "20-35 words describing what this 
                     competitor genuinely does well that 
                     makes them a real threat to us",
  "their_weakness": "20-35 words describing a real gap 
                     or criticism found in the data about 
                     this competitor that we can exploit",
  "campus_cortex_advantage": "20-35 words describing the 
                               specific advantage Campus Cortex 
                               AI has over this competitor 
                               based on our strengths",
  "pricing_signal": "any pricing information detected from 
                     the update, or exactly: Not detected",
  "user_sentiment": "positive or negative or mixed",
  "sentiment_reason": "15-25 words explaining why users feel 
                       this way about the competitor",
  "sales_talking_point": "One powerful sentence a Campus Cortex 
                          sales rep can say when a prospect 
                          mentions this competitor",
  "threat_level": "high or medium or low",
  "recommended_response": "immediate or monitor or ignore",
  "response_action": "20-30 words describing the specific 
                      action Campus Cortex should take in 
                      response to this competitor update"
}}

Rules:
- threat_level: high if impact_level is high, else medium/low
- recommended_response: immediate if threat high, 
  monitor if medium, ignore if low
- user_sentiment: base on tone of the source content
- All string fields: minimum 15 words, never empty string
- pricing_signal: look for any dollar amounts or tier mentions
"""


class BattleCardGenerator:
    
    def __init__(self):
        """Initialize Gemini model for battle card generation."""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-flash-latest")
    
    def generate_all(self, competitor_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate battle cards for all competitor updates.
        Skips competitors with impact_level 'low' to save API calls.
        Returns list of battle card dicts.
        """
        if not competitor_updates:
            print("No competitor updates to generate battle cards for")
            return []
        
        battle_cards = []
        
        for competitor in competitor_updates:
            competitor_name = competitor.get(
                "competitor_name", 
                competitor.get("title", "Unknown Competitor")
            )
            impact_level = competitor.get("impact_level", "medium")
            
            # Skip low-impact competitors to save API quota
            if impact_level == "low":
                print(f"Skipping {competitor_name} (low impact)")
                continue
            
            print(f"Generating battle card: {competitor_name}")
            
            card = self._generate_one(competitor)
            if card:
                battle_cards.append(card)
            
            # Rate limit: wait between cards
            time.sleep(2)
        
        print(f"Generated {len(battle_cards)} battle cards")
        return battle_cards
    
    def _generate_one(self, competitor: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a single battle card for one competitor.
        Returns dict or None on failure.
        """
        competitor_name = competitor.get(
            "competitor_name",
            competitor.get("title", "Unknown")
        )
        description = competitor.get("description", "")
        impact_level = competitor.get("impact_level", "medium")
        
        # Build source context string
        sources = competitor.get("sources", [])
        source_context = " | ".join([
            s.get("source_name", "") for s in sources
        ]) if sources else "EdTech news"
        
        prompt = BATTLE_CARD_PROMPT.format(
            competitor_name=competitor_name,
            competitor_update=description[:800],
            impact_level=impact_level,
            source_context=source_context
        )
        
        for attempt in range(2):
            try:
                response = self.model.generate_content(prompt)
                raw = response.text.strip()
                
                # Clean markdown fences
                raw = re.sub(r'```json\s*', '', raw)
                raw = re.sub(r'```\s*', '', raw)
                raw = raw.strip()
                
                # Extract JSON
                start = raw.find('{')
                end = raw.rfind('}') + 1
                if start == -1 or end == 0:
                    raise ValueError("No JSON in response")
                
                card = json.loads(raw[start:end])
                
                # Validate required fields exist
                required = [
                    "their_strength", "their_weakness",
                    "campus_cortex_advantage", "threat_level",
                    "sales_talking_point", "recommended_response"
                ]
                for field in required:
                    if field not in card or not card[field]:
                        card[field] = "Analysis pending. Retry."
                
                # Ensure competitor_name is correct
                card["competitor_name"] = competitor_name
                
                # Add source URLs from original competitor data
                card["sources"] = competitor.get("sources", [])
                
                return card
            
            except json.JSONDecodeError as e:
                print(f"Battle card JSON error {competitor_name} "
                      f"attempt {attempt+1}: {e}")
                time.sleep(2)
            
            except Exception as e:
                print(f"Battle card error {competitor_name} "
                      f"attempt {attempt+1}: {e}")
                time.sleep(2)
        
        # Return minimal fallback card instead of None
        return {
            "competitor_name": competitor_name,
            "their_strength": "Analysis unavailable. Retry pipeline.",
            "their_weakness": "Analysis unavailable. Retry pipeline.",
            "campus_cortex_advantage": ("Campus Cortex AI offers "
                "streamlined onboarding and unified workflows. "
                "Detailed analysis pending."),
            "pricing_signal": "Not detected",
            "user_sentiment": "mixed",
            "sentiment_reason": "Insufficient data for analysis.",
            "sales_talking_point": ("Campus Cortex AI provides "
                "a unified, affordable alternative."),
            "threat_level": competitor.get("impact_level", "medium"),
            "recommended_response": "monitor",
            "response_action": "Monitor competitor activity and retry.",
            "sources": competitor.get("sources", []),
            "_generated": False
        }

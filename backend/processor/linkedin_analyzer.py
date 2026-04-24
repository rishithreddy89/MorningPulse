"""LinkedIn post analyzer using Gemini for competitive intelligence."""

import json
import os
import re
import time
from datetime import date
from typing import Dict, List

import google.generativeai as genai


LINKEDIN_ANALYSIS_PROMPT = """
CRITICAL: Return ONLY a raw JSON object. Start with {{ end with }}. No markdown. No explanation. No code fences.

You are a competitive intelligence analyst for Campus Cortex AI, an EdTech SaaS startup.

Analyze these LinkedIn company posts from EdTech competitors. Extract structured insights about what competitors are doing.

Return this exact JSON:
{{
  "scraped_at": "{date}",
  "competitor_activities": [
    {{
      "competitor_name": "exact company name",
      "activity_type": "product_launch or partnership or hiring or event or thought_leadership",
      "title": "4-8 word title of what they posted about",
      "description": "20-35 words explaining what they posted, why it matters, and what it signals about their strategy",
      "signal_strength": "high or medium or low",
      "our_response": "15-25 words — what Campus Cortex AI should do in response to this activity",
      "source_url": "url of the post"
    }}
  ],
  "market_signals": [
    {{
      "signal": "4-6 word signal name",
      "explanation": "20-30 words explaining what this pattern across multiple competitor posts signals about where the EdTech market is heading",
      "implications": "15-25 words on what this means for Campus Cortex AI strategy"
    }}
  ],
  "summary": "3 sentences summarizing the most important competitive intelligence from LinkedIn today. Be specific about companies and strategies."
}}

Rules:
- Maximum 5 items in competitor_activities
- Maximum 3 items in market_signals
- activity_type must be exactly one of the listed values
- signal_strength must be exactly: high, medium, or low
- Every field minimum 15 words, never empty string
- Only include posts that reveal actual company strategy

LINKEDIN POSTS TO ANALYZE:
{context}
"""


class LinkedInAnalyzer:
    
    def __init__(self):
        """Initialize Gemini model for LinkedIn analysis."""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-flash-latest")
    
    def analyze(self, posts: List[Dict]) -> Dict:
        """Analyze LinkedIn posts and return structured intelligence."""
        if not posts:
            return self._empty_result()
        
        context_lines = []
        for post in posts:
            line = (
                f"COMPANY: {post.get('competitor_name', post.get('source', ''))}\n"
                f"TEXT: {post.get('summary', '')}\n"
                f"URL: {post.get('url', '')}\n"
                f"---"
            )
            context_lines.append(line)
        
        context = "\n".join(context_lines)[:15000]
        
        prompt = LINKEDIN_ANALYSIS_PROMPT.format(
            date=date.today().isoformat(),
            context=context
        )
        
        for attempt in range(3):
            try:
                response = self.model.generate_content(prompt)
                raw = response.text.strip()
                
                raw = re.sub(r'```json\s*', '', raw)
                raw = re.sub(r'```\s*', '', raw)
                raw = raw.strip()
                
                start = raw.find('{')
                end = raw.rfind('}') + 1
                if start == -1 or end == 0:
                    raise ValueError("No JSON found")
                
                result = json.loads(raw[start:end])
                print("LinkedIn analysis complete")
                return result
            
            except json.JSONDecodeError as e:
                print(f"LinkedIn analysis JSON error attempt {attempt+1}: {e}")
                time.sleep(3)
            except Exception as e:
                print(f"LinkedIn analysis error attempt {attempt+1}: {e}")
                time.sleep(3)
        
        return self._empty_result()
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            "scraped_at": date.today().isoformat(),
            "competitor_activities": [],
            "market_signals": [],
            "summary": "No LinkedIn data available. Trigger a scrape."
        }

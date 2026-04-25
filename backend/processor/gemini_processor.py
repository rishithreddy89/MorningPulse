"""Gemini-based EdTech intelligence extraction with robust error handling."""

import json
import re
import time
from datetime import date
from typing import Any, Dict, List

import google.generativeai as genai

import config


def extract_json(raw_text: str) -> dict:
    """Extract JSON from Gemini response robustly."""
    cleaned = re.sub(r'```json\s*', '', raw_text)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()
    
    start = cleaned.find('{')
    if start == -1:
        raise ValueError("No JSON object found")
    
    depth = 0
    end = -1
    for i, ch in enumerate(cleaned[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    if end == -1:
        raise ValueError("Unmatched braces - truncated JSON")
    
    json_str = cleaned[start:end]
    return json.loads(json_str)


GEMINI_PROMPT = """
CRITICAL: Your entire response must be ONLY a JSON object.
First character must be {{ and last character must be }}.
Zero text before or after. Zero markdown. Zero explanation.

You are a senior competitive intelligence analyst for Campus Cortex AI, an EdTech SaaS startup.

Analyze the {post_count} posts below. Extract intelligence.

════════════════════════════════════════════════════════════════════════════
CLASSIFICATION RULES (CRITICAL - READ CAREFULLY):
════════════════════════════════════════════════════════════════════════════

COMPETITOR UPDATES - ONLY include if a company takes DIRECT ACTION:
✅ INCLUDE:
  - Acquisitions ("Company X acquires Company Y")
  - Funding rounds ("Company X raises $50M Series B")
  - Product launches ("Company X launches new AI grading tool")
  - Partnerships ("Company X partners with School District Y")
  - Major hires ("Company X hires former Google exec as CTO")
  - Feature releases ("Company X adds video conferencing to platform")
  - Pricing changes ("Company X cuts prices by 30%")
  - Market expansion ("Company X enters European market")

❌ DO NOT INCLUDE:
  - General market trends ("EdTech companies are focusing on AI")
  - Regulatory discussions ("New privacy laws may affect EdTech")
  - User complaints ("Teachers frustrated with tool complexity")
  - Industry analysis ("Market consolidation accelerating")
  - Opinion pieces ("Why EdTech needs to change")

EMERGING TRENDS - Industry-wide patterns:
✅ INCLUDE:
  - Technology adoption patterns ("AI tutoring gaining traction")
  - Market movements ("Shift toward privacy-first design")
  - Regulatory changes ("New data privacy requirements")
  - Behavioral shifts ("Teachers preferring mobile-first tools")
  - Industry consolidation ("Wave of EdTech acquisitions")

USER PAIN POINTS - Problems teachers/students face:
✅ INCLUDE:
  - Tool complexity issues
  - Integration problems
  - Cost concerns
  - Training gaps
  - Performance issues

════════════════════════════════════════════════════════════════════════════
DEDUPLICATION RULES (CRITICAL):
════════════════════════════════════════════════════════════════════════════

1. If multiple posts describe THE SAME EVENT:
   - Merge them into ONE update
   - Combine sources
   - Use the most detailed description
   
   Example:
   Post 1: "ClassDojo raises $50M"
   Post 2: "ClassDojo secures Series C funding of $50M"
   → ONE update: "ClassDojo raises $50M Series C"

2. Each competitor should appear ONCE unless they have MULTIPLE DISTINCT EVENTS:
   - ✅ OK: ClassDojo raises funding + ClassDojo launches feature
   - ❌ NOT OK: ClassDojo raises funding (mentioned twice)

3. Remove generic "Market Signal" entries:
   - Only include if it's a SPECIFIC industry trend
   - Not a catch-all for unclassified posts

════════════════════════════════════════════════════════════════════════════
OUTPUT REQUIREMENTS:
════════════════════════════════════════════════════════════════════════════

- competitor_updates: 0-5 items (ONLY real company actions)
- emerging_tech_trends: 3-5 items (industry patterns)
- user_pain_points: 2-4 items (teacher/student problems)

- Each competitor_name must be a REAL company name (not "Market Signal")
- Each update must map to ONE specific event
- No duplicate companies unless DIFFERENT events
- No duplicate events

KEYWORD CONTEXT (use this to identify trends):
{keyword_context}

COMPETITOR GROUPING:
{competitor_grouping}

════════════════════════════════════════════════════════════════════════════
FIELD RULES:
════════════════════════════════════════════════════════════════════════════
- "issue", "context", "description", "explanation" fields:
  MINIMUM 20 words each. NEVER empty string. NEVER null.
  If info is limited, write what you know and append: "Further monitoring recommended."
- "title", "trend" fields: 4 to 8 words exactly
- "sources": at least 1 item per entry always
- competitor_name: MUST be a real company name from posts (not "Market Signal")

Return this exact structure:
{{
  "date": "{date}",
  "user_pain_points": [
    {{
      "issue": "4-8 word title of the pain",
      "context": "Minimum 20 words explaining what teachers struggle with, why it hurts productivity, and what they wish existed instead.",
      "sources": [{{"url": "exact url", "source_name": "site name"}}]
    }}
  ],
  "competitor_updates": [
    {{
      "competitor_name": "Exact Company Name (MUST be real company)",
      "title": "4-8 word title of their SPECIFIC ACTION",
      "description": "Minimum 20 words describing what SPECIFIC ACTION this competitor took, why it matters to the EdTech market, and who it affects.",
      "impact_level": "high",
      "sources": [{{"url": "exact url", "source_name": "site name"}}]
    }}
  ],
  "emerging_tech_trends": [
    {{
      "trend": "4-6 word trend name",
      "explanation": "Minimum 20 words explaining what this INDUSTRY-WIDE trend is, why it is growing right now, and what it means for EdTech companies.",
      "volume": 5,
      "sources": [{{"url": "exact url", "source_name": "site name"}}]
    }}
  ]
}}

impact_level must be exactly one of: high, medium, low
volume must be an integer (estimated posts about this topic)

POSTS TO ANALYZE:
{context}
"""


class GeminiProcessor:
    """Process EdTech posts into structured intelligence using Gemini."""

    def __init__(self) -> None:
        """Configure Gemini SDK client and model."""
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        print("[GeminiProcessor] Gemini processor initialized")

    def process(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process posts through Gemini with retry and validation."""
        if len(posts) > 35:
            mid = len(posts) // 2
            d1 = self._process_chunk(posts[:mid])
            d2 = self._process_chunk(posts[mid:])
            return self._merge(d1, d2)
        
        return self._process_chunk(posts)

    def _process_chunk(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Single chunk processing with 3 attempts."""
        # ════════════════════════════════════════════════════════════════════
        # PREPROCESSING: Group by competitor and extract keywords
        # ════════════════════════════════════════════════════════════════════
        competitor_groups = self._group_by_competitor(posts)
        keyword_frequencies = self._extract_keyword_frequencies(posts)
        
        # Build context strings
        context = self._build_context(posts)
        keyword_context = self._build_keyword_context(keyword_frequencies)
        competitor_grouping = self._build_competitor_grouping(competitor_groups)
        
        prompt = GEMINI_PROMPT.format(
            post_count=len(posts),
            date=date.today().isoformat(),
            context=context,
            keyword_context=keyword_context,
            competitor_grouping=competitor_grouping
        )
        
        last_error = None
        for attempt in range(3):
            try:
                response = self.model.generate_content(prompt)
                parsed = extract_json(response.text)
                validated = self._validate(parsed)
                print(f"Gemini success on attempt {attempt + 1}")
                return validated
            
            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                print(f"Attempt {attempt+1} failed: {e}")
                time.sleep(3 * (attempt + 1))
            
            except Exception as e:
                last_error = e
                print(f"Gemini API error attempt {attempt+1}: {e}")
                time.sleep(5)
        
        print(f"All attempts failed: {last_error}")
        return self._default_digest()

    def _validate(self, parsed: dict) -> dict:
        """Ensure no empty fields, deduplicate, and enforce classification rules."""
        
        # ════════════════════════════════════════════════════════════════
        # STEP 1: Clean and validate competitor updates
        # ════════════════════════════════════════════════════════════════
        competitor_updates = []
        seen_events = set()  # Track unique events
        seen_companies = {}  # Track companies and their events
        
        for c in parsed.get("competitor_updates", []):
            # Normalize field names
            if "name" in c and "competitor_name" not in c:
                c["competitor_name"] = c.pop("name")
            if "explanation" in c and "description" not in c:
                c["description"] = c.pop("explanation")
            
            competitor_name = c.get("competitor_name", "").strip()
            title = c.get("title", "").strip()
            description = c.get("description", "").strip()
            
            # ════════════════════════════════════════════════════════════
            # CLASSIFICATION RULE: Only include DIRECT company actions
            # ════════════════════════════════════════════════════════════
            
            # Skip if no real company name
            if not competitor_name or competitor_name.lower() in ["market signal", "industry trend", "unknown", "market_signal"]:
                print(f"[Classifier] Skipping non-company update: {title}")
                continue
            
            # Skip if it's a general trend (not a specific action)
            trend_keywords = ["trend", "movement", "shift", "pattern", "growing", "increasing", "industry"]
            if any(keyword in title.lower() for keyword in trend_keywords):
                print(f"[Classifier] Moving to trends: {title}")
                continue
            
            # Skip if it's a user pain point
            pain_keywords = ["struggle", "frustrated", "problem", "issue", "challenge", "difficulty"]
            if any(keyword in title.lower() for keyword in pain_keywords):
                print(f"[Classifier] Moving to pain points: {title}")
                continue
            
            # ════════════════════════════════════════════════════════════
            # DEDUPLICATION: Check for duplicate events
            # ════════════════════════════════════════════════════════════
            
            # Create event signature for deduplication
            event_signature = f"{competitor_name.lower()}:{title.lower()[:30]}"
            
            if event_signature in seen_events:
                print(f"[Dedup] Skipping duplicate event: {competitor_name} - {title}")
                continue
            
            # Check if company already has an update
            if competitor_name in seen_companies:
                # Allow multiple updates only if they're DIFFERENT events
                existing_titles = seen_companies[competitor_name]
                
                # Check similarity
                is_duplicate = False
                for existing_title in existing_titles:
                    # Simple similarity check
                    common_words = set(title.lower().split()) & set(existing_title.lower().split())
                    if len(common_words) >= 2:  # If 2+ words match, likely duplicate
                        print(f"[Dedup] Skipping similar event for {competitor_name}: {title}")
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    continue
                
                seen_companies[competitor_name].append(title)
            else:
                seen_companies[competitor_name] = [title]
            
            seen_events.add(event_signature)
            
            # ════════════════════════════════════════════════════════════
            # VALIDATION: Ensure minimum field requirements
            # ════════════════════════════════════════════════════════════
            
            if len(description) < 20:
                description = (
                    f"{competitor_name} "
                    f"made an update related to {title}. "
                    "Further monitoring recommended."
                )
            
            if "impact_level" not in c:
                c["impact_level"] = "medium"
            
            c["competitor_name"] = competitor_name
            c["title"] = title
            c["description"] = description
            
            competitor_updates.append(c)
        
        parsed["competitor_updates"] = competitor_updates[:5]  # Max 5
        
        print(f"[Classifier] Competitor updates after dedup: {len(competitor_updates)}")
        
        # ════════════════════════════════════════════════════════════════
        # STEP 2: Validate emerging trends
        # ════════════════════════════════════════════════════════════════
        for t in parsed.get("emerging_tech_trends", []):
            if "description" in t and "explanation" not in t:
                t["explanation"] = t.pop("description")
            if len(t.get("explanation", "")) < 20:
                t["explanation"] = (
                    f"The trend '{t.get('trend','')}' is gaining "
                    "traction in the EdTech space. "
                    "Further monitoring recommended."
                )
            if "volume" not in t:
                t["volume"] = 1
        
        # ════════════════════════════════════════════════════════════════
        # STEP 3: Validate user pain points
        # ════════════════════════════════════════════════════════════════
        for p in parsed.get("user_pain_points", []):
            if len(p.get("context", "")) < 20:
                p["context"] = (
                    f"Teachers are experiencing challenges with "
                    f"{p.get('issue','')}. "
                    "Further monitoring recommended."
                )
        
        return parsed

    def _build_context(self, posts: list) -> str:
        """Format posts into context string, hard cap at 18000 chars."""
        lines = []
        for p in posts:
            line = (
                f"SOURCE: {p.get('source','unknown')} | "
                f"TITLE: {p.get('title','')} | "
                f"CONTENT: {p.get('summary', p.get('content',''))[:350]} | "
                f"URL: {p.get('url','')} | "
                f"COMPETITOR: {p.get('detected_competitor', 'unknown')}"
            )
            lines.append(line)
        
        full = "\n---\n".join(lines)
        if len(full) > 18000:
            full = full[:18000]
            print(f"Context truncated to 18000 chars")
        return full
    
    def _group_by_competitor(self, posts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group posts by detected competitor."""
        groups = {}
        
        for post in posts:
            competitor = post.get("detected_competitor", "market_signal")
            if competitor not in groups:
                groups[competitor] = []
            groups[competitor].append(post)
        
        return groups
    
    def _extract_keyword_frequencies(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract keyword frequencies for trend detection."""
        from collections import Counter
        import re
        
        keywords = []
        
        for post in posts:
            title = post.get("title", "").lower()
            summary = post.get("summary", "").lower()
            text = f"{title} {summary}"
            
            # Extract meaningful words (3+ chars)
            words = re.findall(r'\b[a-z]{3,}\b', text)
            keywords.extend(words)
        
        # Count frequencies
        counter = Counter(keywords)
        
        # Filter common words
        common = {"the", "and", "for", "with", "this", "that", "from", "have", "been", "will", "are", "was"}
        filtered = {k: v for k, v in counter.items() if k not in common and v >= 2}
        
        return dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:15])
    
    def _build_keyword_context(self, keywords: Dict[str, int]) -> str:
        """Build keyword context string for Gemini."""
        if not keywords:
            return "No significant keywords detected."
        
        lines = [f"- {keyword}: {count} mentions" for keyword, count in keywords.items()]
        return "\n".join(lines)
    
    def _build_competitor_grouping(self, groups: Dict[str, List[Dict[str, Any]]]) -> str:
        """Build competitor grouping string for Gemini."""
        if not groups:
            return "No competitors detected."
        
        lines = []
        for competitor, posts in groups.items():
            lines.append(f"- {competitor}: {len(posts)} posts")
        
        return "\n".join(lines)

    def _merge(self, d1: dict, d2: dict) -> dict:
        """Merge two digest chunks, deduplicate by competitor name."""
        merged = {
            "date": d1.get("date", date.today().isoformat()),
            "user_pain_points": (
                d1.get("user_pain_points", []) + 
                d2.get("user_pain_points", [])
            )[:5],
            "emerging_tech_trends": (
                d1.get("emerging_tech_trends", []) + 
                d2.get("emerging_tech_trends", [])
            )[:5],
            "competitor_updates": [],
        }
        seen = set()
        for c in (d1.get("competitor_updates", []) + 
                  d2.get("competitor_updates", [])):
            name = c.get("competitor_name", "unknown").lower()
            if name not in seen:
                seen.add(name)
                merged["competitor_updates"].append(c)
            if len(merged["competitor_updates"]) >= 5:
                break
        return merged

    def _default_digest(self) -> dict:
        return {
            "date": date.today().isoformat(),
            "user_pain_points": [],
            "competitor_updates": [],
            "emerging_tech_trends": [],
            "_pipeline_error": True,
            "_message": "Gemini processing failed. Check logs."
        }

    def generate_weekly_memo(self, digests: List[Dict[str, Any]]) -> str:
        """Generate weekly strategy memo from multiple digests."""
        try:
            response = self.model.generate_content(
                retry_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4000,
                    temperature=0.3,
                    response_mime_type="application/json",
                )
            )
            raw_text = self._clean_response(getattr(response, "text", "") or "")
            parsed = self._safe_parse_json(raw_text)
            parsed = self._fix_gemini_structure(parsed)
            return self._normalize_output(parsed)
        except Exception as exc:
            print(f"[GeminiProcessor] Retry failed: {exc}")
            return self._heuristic_output(posts)

    def _fix_gemini_structure(self, digest: dict) -> dict:
        """
        Gemini consistently puts full text in label fields and leaves
        explanation fields empty. This function fixes that by:
        1. Moving long label text → explanation field
        2. Creating a short label from the first few words
        3. Recovering empty competitor_updates from source names
        """
        def make_short_label(text: str, max_words: int = 5) -> str:
            """Extract first N meaningful words as a short label."""
            text = text.rstrip(".,;:")
            words = text.split()
            if len(words) <= max_words:
                return text
            return " ".join(words[:max_words])

        # ── Fix user_pain_points ──────────────────────────────────────────
        for item in digest.get("user_pain_points", []):
            issue = (item.get("issue") or "").strip()
            context = (item.get("context") or "").strip()

            # If context is empty but issue is long → Gemini put it in wrong field
            if not context and len(issue.split()) > 7:
                item["context"] = issue
                item["issue"] = make_short_label(issue)
                print(f"[Fix] Moved pain point text → context: '{item['issue']}'")

            # If both empty, set placeholder
            if not item.get("context", "").strip():
                item["context"] = item.get("issue", "See source for details.")

        # ── Fix emerging_tech_trends ──────────────────────────────────────
        for item in digest.get("emerging_tech_trends", []):
            trend = (item.get("trend") or "").strip()
            explanation = (item.get("explanation") or "").strip()

            if not explanation and len(trend.split()) > 7:
                item["explanation"] = trend
                item["trend"] = make_short_label(trend)
                print(f"[Fix] Moved trend text → explanation: '{item['trend']}'")

            if not item.get("explanation", "").strip():
                item["explanation"] = item.get("trend", "See source for details.")

        # ── Fix competitor_updates ────────────────────────────────────────
        for item in digest.get("competitor_updates", []):
            title = (item.get("title") or "").strip()
            description = (item.get("description") or "").strip()

            # If title long and description empty → move it
            if not description and len(title.split()) > 7:
                item["description"] = title
                item["title"] = make_short_label(title)
                print(f"[Fix] Moved competitor text → description: '{item['title']}'")

            # If title completely empty, recover from source_name
            if not item.get("title", "").strip():
                sources = item.get("sources", [])
                if sources:
                    raw = sources[0].get("source_name", "Competitor Update")
                    item["title"] = make_short_label(raw)
                    print(f"[Fix] Recovered competitor title from source: '{item['title']}'")

            # If description still empty, use title as fallback
            if not item.get("description", "").strip():
                item["description"] = item.get("title", "See source article for details.")

        return digest

    def _validate_and_fix_structure(self, digest: Dict[str, Any]) -> Dict[str, Any]:
        """Fix cases where Gemini puts full text in label field and leaves explanation empty."""
        
        # Fix user_pain_points
        for item in digest.get("user_pain_points", []):
            issue = item.get("issue", "")
            context = item.get("context", "")
            
            # If issue is long (>8 words) and context is empty → Gemini put it in wrong field
            if len(issue.split()) > 8 and not context.strip():
                # Move full text to context, create short label from first 4 words
                item["context"] = issue
                item["issue"] = " ".join(issue.split()[:4]).rstrip(".,") + "..."
                print(f"[Validator] Fixed misplaced issue: {item['issue']}")
        
        # Fix emerging_tech_trends
        for item in digest.get("emerging_tech_trends", []):
            trend = item.get("trend", "")
            explanation = item.get("explanation", "")
            
            if len(trend.split()) > 8 and not explanation.strip():
                item["explanation"] = trend
                item["trend"] = " ".join(trend.split()[:4]).rstrip(".,") + "..."
                print(f"[Validator] Fixed misplaced trend: {item['trend']}")
        
        # Fix competitor_updates
        for item in digest.get("competitor_updates", []):
            title = item.get("title", "")
            description = item.get("description", "")
            
            if not title.strip() and not description.strip():
                # Pull from source_name as last resort
                sources = item.get("sources", [])
                if sources:
                    item["title"] = sources[0].get("source_name", "Competitor Update")[:50]
                    item["description"] = f"See source article for details: {item['title']}"
                    print(f"[Validator] Recovered empty competitor update from source name")
            elif len(title.split()) > 8 and not description.strip():
                item["description"] = title
                item["title"] = " ".join(title.split()[:4]).rstrip(".,")
                print(f"[Validator] Fixed misplaced title: {item['title']}")
        
        print("[Validator] Structure validation complete")
        return digest

    def _validate_and_fix_digest(self, digest: Dict[str, Any], posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for empty explanation fields and retry if needed."""
        empty_trends = [
            item for item in digest.get("emerging_tech_trends", [])
            if not item.get("explanation", "").strip()
        ]
        
        if not empty_trends:
            print("[Validator] All explanations present ✅")
            return digest
        
        print(f"[Validator] Found {len(empty_trends)} trends with empty explanation. Retrying...")
        
        # Build targeted retry prompt
        trend_names = [item["trend"] for item in empty_trends]
        context_snippets = [f"{p.get('title', '')}: {p.get('summary', '')[:200]}" for p in posts[:10]]
        
        retry_prompt = f"""
The following EdTech trends need a 2-3 sentence explanation each.
For each trend, explain what it is, why it matters, and what is driving it.

Trends to explain: {trend_names}

Context from articles:
{context_snippets}

Respond ONLY with valid JSON in this format:
{{
  "explanations": [
    {{"trend": "trend name here", "explanation": "2-3 sentences here"}}
  ]
}}
"""
        
        try:
            retry_response = self.model.generate_content(
                retry_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.7,
                )
            )
            retry_text = self._clean_response(getattr(retry_response, "text", "") or "")
            retry_data = json.loads(retry_text)
            
            # Merge explanations back
            explanation_map = {
                item["trend"]: item["explanation"]
                for item in retry_data.get("explanations", [])
            }
            
            for trend_item in digest["emerging_tech_trends"]:
                if not trend_item.get("explanation", "").strip():
                    trend_name = trend_item["trend"]
                    if trend_name in explanation_map:
                        trend_item["explanation"] = explanation_map[trend_name]
                        print(f"[Validator] Fixed explanation for: {trend_name}")
            
        except Exception as e:
            print(f"[Validator] Retry failed: {e}")
        
        return digest

    def _normalize_output(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Gemini output into the exact EdTech digest shape with source attribution."""
        competitor_updates_raw = payload.get("competitor_updates") or []
        user_pain_points_raw = payload.get("user_pain_points") or payload.get("pain_points") or []
        emerging_tech_trends_raw = payload.get("emerging_tech_trends") or payload.get("trends") or []

        competitor_updates: List[Dict[str, Any]] = []
        for item in competitor_updates_raw:
            if not isinstance(item, dict):
                continue
            sources = self._normalize_sources(item.get("sources", []))
            competitor_updates.append(
                {
                    "title": str(item.get("title", "")).strip(),
                    "description": str(item.get("description", "")).strip(),
                    "sources": sources,
                }
            )

        user_pain_points: List[Dict[str, Any]] = []
        for item in user_pain_points_raw:
            if not isinstance(item, dict):
                continue
            sources = self._normalize_sources(item.get("sources", []))
            user_pain_points.append(
                {
                    "issue": str(item.get("issue", item.get("pain_point", ""))).strip(),
                    "context": str(item.get("context", "")).strip(),
                    "sources": sources,
                }
            )

        emerging_tech_trends: List[Dict[str, Any]] = []
        for item in emerging_tech_trends_raw:
            if not isinstance(item, dict):
                continue
            sources = self._normalize_sources(item.get("sources", []))
            emerging_tech_trends.append(
                {
                    "trend": str(item.get("trend", item.get("name", ""))).strip(),
                    "explanation": str(item.get("explanation", "")).strip(),
                    "sources": sources,
                }
            )

        return {
            "competitor_updates": competitor_updates,
            "user_pain_points": user_pain_points,
            "emerging_tech_trends": emerging_tech_trends,
        }

    def _normalize_sources(self, sources_raw: Any) -> List[Dict[str, str]]:
        """Normalize and validate source attribution, mapping URLs from input posts."""
        sources: List[Dict[str, str]] = []
        
        if isinstance(sources_raw, list):
            for source in sources_raw:
                if isinstance(source, dict):
                    source_name = str(source.get("source_name", "")).strip()
                    if source_name:
                        # Map URL from input posts, never trust Gemini URLs
                        url = self._map_source_url(source_name)
                        sources.append({"source_name": source_name, "url": url})
        
        # Fallback: if no valid sources, use top input posts
        if not sources and hasattr(self, "_input_posts") and self._input_posts:
            fallback_sources = [
                {
                    "source_name": post.get("source_label", post.get("source", "Unknown")),
                    "url": post.get("url") or post.get("link") or "#",
                }
                for post in self._input_posts[:2]
            ]
            sources = fallback_sources
        
        return sources

    def _build_title_url_map(self, posts: List[Dict[str, Any]]) -> None:
        """Build a mapping of post titles to URLs for source attribution."""
        self._title_url_map: Dict[str, str] = {}
        self._source_label_url_map: Dict[str, str] = {}
        
        print("[Source Mapping] Building title → URL map")
        
        for post in posts:
            title = str(post.get("title", "")).lower().strip()
            # Try multiple field names for URL
            url = post.get("url") or post.get("link") or post.get("href") or ""
            source_label = str(post.get("source_label", "")).lower().strip()
            
            # Only add if URL is valid
            if title and url and isinstance(url, str) and url.startswith("http"):
                self._title_url_map[title] = url
            
            if source_label and url and isinstance(url, str) and url.startswith("http"):
                # Store first URL for each source label
                if source_label not in self._source_label_url_map:
                    self._source_label_url_map[source_label] = url
        
        print(f"[Source Mapping] Mapped {len(self._title_url_map)} titles to URLs")
        
        # Debug: Show sample mappings
        if self._title_url_map:
            print("[Source Mapping] Sample mappings:")
            for title, url in list(self._title_url_map.items())[:5]:
                print(f"  {title[:60]}... → {url}")
        else:
            print("[Source Mapping] WARNING: No titles mapped! Check post structure.")

    def _map_source_url(self, source_name: str) -> str:
        """Map a source name to its URL from input posts using fuzzy matching."""
        if not source_name:
            return "#"
        
        source_lower = source_name.lower().strip()
        
        # Remove N/A or invalid URLs
        if source_lower in ["n/a", "unknown"]:
            return "#"
        
        # Try exact title match
        if source_lower in self._title_url_map:
            matched_url = self._title_url_map[source_lower]
            if matched_url and matched_url.startswith("http"):
                return matched_url
        
        # Try source label match
        if source_lower in self._source_label_url_map:
            matched_url = self._source_label_url_map[source_lower]
            if matched_url and matched_url.startswith("http"):
                return matched_url
        
        # Try fuzzy match on titles (improved)
        for title, url in self._title_url_map.items():
            # Check if source name is in title or title is in source name
            if (source_lower in title or title in source_lower) and url.startswith("http"):
                return url
        
        # Try fuzzy match on source labels
        for label, url in self._source_label_url_map.items():
            if (source_lower in label or label in source_lower) and url.startswith("http"):
                return url
        
        # No match found - return # (frontend will handle)
        return "#"

    def _heuristic_output(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return a lightweight fallback summary when Gemini is unavailable."""
        competitor_updates: List[Dict[str, Any]] = []
        for post in posts[:3]:
            competitor_updates.append(
                {
                    "title": str(post.get("title", "")).strip(),
                    "description": "Potential EdTech competitor signal captured from current source coverage.",
                    "sources": [
                        {
                            "source_name": post.get("source_label", post.get("source", "Unknown")),
                            "url": post.get("url") or post.get("link") or "#",
                        }
                    ],
                }
            )

        return {
            "competitor_updates": competitor_updates,
            "user_pain_points": [],
            "emerging_tech_trends": [],
        }

    def _default_output(self) -> Dict[str, Any]:
        """Return a safe empty output when no posts are available."""
        return {
            "competitor_updates": [],
            "user_pain_points": [],
            "emerging_tech_trends": [],
        }

    def generate_weekly_memo(self, weekly_digests: List[Dict[str, Any]]) -> str:
        """Generate a concise weekly memo from EdTech digest snapshots."""
        digest_summaries: List[str] = []
        for digest in weekly_digests:
            competitor_updates = digest.get("competitor_updates", [])
            pain_points = digest.get("user_pain_points", [])
            trends = digest.get("emerging_tech_trends", [])

            top_competitor = (
                competitor_updates[0].get("title", "No major competitor update")
                if competitor_updates
                else "No major competitor update"
            )
            top_pain_point = (
                pain_points[0].get("issue", "No major pain point") if pain_points else "No major pain point"
            )
            top_trend = trends[0].get("trend", "No major trend") if trends else "No major trend"

            digest_summaries.append(
                "\n".join(
                    [
                        f"- Date: {digest.get('date', 'unknown')}",
                        f"- Top competitor update: {top_competitor}",
                        f"- Top pain point: {top_pain_point}",
                        f"- Top trend: {top_trend}",
                    ]
                )
            )

        weekly_context = "\n\n".join(digest_summaries)

        prompt = f"""
You are a strategy consultant for an EdTech market intelligence team.
Analyze these daily EdTech digests and write a concise weekly memo.

Cover in order:
1. Biggest competitor moves this week
2. Most repeated user pain points
3. Strongest emerging trends
4. Overall market movement
5. Top 3 strategic recommendations for next week

Be specific and use professional prose.

DIGESTS:
{weekly_context}
"""

        try:
            response = self.model.generate_content(prompt)
            return (getattr(response, "text", "") or "").strip()
        except Exception as exc:
            print(f"[GeminiProcessor] Weekly memo generation failed: {exc}")
            return "Weekly memo generation failed. Please retry."

"""Customer Risk Alert System - Detects competitor threats to customer retention."""

from typing import Any, Dict, List
import re


class CustomerRiskAnalyzer:
    """Analyze competitor actions for customer retention risks."""

    # Threat trigger keywords with base scores
    THREAT_TRIGGERS = {
        "free": 4,
        "price drop": 4,
        "discount": 4,
        "pricing": 3,
        "acquired": 3,
        "acquisition": 3,
        "partnership": 3,
        "launched": 2,
        "raised funding": 2,
        "new feature": 2,
        "expansion": 2,
        "integration": 2,
    }

    # Customer segment keywords
    SEGMENT_KEYWORDS = [
        "k-12", "k12", "district", "school", "teacher", "student",
        "classroom", "education", "edtech"
    ]

    # Competitor names (EdTech space)
    KNOWN_COMPETITORS = [
        "powerschool", "canvas", "schoology", "google classroom",
        "classdojo", "remind", "seesaw", "clever", "classlink",
        "blackboard", "moodle", "edmodo", "kahoot", "quizlet"
    ]

    def __init__(self):
        """Initialize the risk analyzer."""
        print("[CustomerRisk] Risk analyzer initialized")

    def analyze(self, posts: List[Dict[str, Any]], digest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze posts and digest for customer risk alerts.
        
        Args:
            posts: Raw posts from all sources
            digest: Processed digest with competitor updates
            
        Returns:
            List of risk alerts sorted by risk score (highest first)
        """
        print(f"[CustomerRisk] Analyzing {len(posts)} posts for customer risks")
        
        alerts = []
        seen_events = set()  # Deduplication
        
        # Analyze competitor updates from digest (primary source)
        competitor_updates = digest.get("competitor_updates", [])
        for update in competitor_updates:
            alert = self._analyze_competitor_update(update)
            if alert and alert["risk_score"] >= 4:
                event_key = f"{alert['company'].lower()}:{alert['event'][:30].lower()}"
                if event_key not in seen_events:
                    alerts.append(alert)
                    seen_events.add(event_key)
        
        # Analyze raw posts for additional signals
        for post in posts:
            alert = self._analyze_post(post)
            if alert and alert["risk_score"] >= 4:
                event_key = f"{alert['company'].lower()}:{alert['event'][:30].lower()}"
                if event_key not in seen_events:
                    alerts.append(alert)
                    seen_events.add(event_key)
        
        # Sort by risk score (highest first)
        alerts.sort(key=lambda x: x["risk_score"], reverse=True)
        
        # Keep only top 5 highest risk alerts
        alerts = alerts[:5]
        
        print(f"[CustomerRisk] Found {len(alerts)} customer risk alerts")
        for alert in alerts:
            print(f"  - {alert['company']}: {alert['event']} (score: {alert['risk_score']})")
        
        return alerts

    def _analyze_competitor_update(self, update: Dict[str, Any]) -> Dict[str, Any] | None:
        """Analyze a competitor update for customer risk."""
        title = update.get("title", "").lower()
        description = update.get("description", "").lower()
        competitor_name = update.get("competitor_name", "")
        
        if not competitor_name or not title:
            return None
        
        # Check for threat triggers
        risk_score = 0
        matched_triggers = []
        
        combined_text = f"{title} {description}"
        
        for trigger, score in self.THREAT_TRIGGERS.items():
            if trigger in combined_text:
                risk_score += score
                matched_triggers.append(trigger)
        
        # Check for customer segment overlap
        segment_match = any(keyword in combined_text for keyword in self.SEGMENT_KEYWORDS)
        if segment_match:
            risk_score += 3
        
        # Source credibility (from digest = high credibility)
        risk_score += 2
        
        # Cap at 10
        risk_score = min(risk_score, 10)
        
        # Only return if score >= 4
        if risk_score < 4:
            return None
        
        # Determine risk level
        if risk_score >= 7:
            risk_level = "High"
        elif risk_score >= 4:
            risk_level = "Medium"
        else:
            return None
        
        # Extract event description
        event = self._extract_event(title, description, matched_triggers)
        
        # Generate why it matters
        why_it_matters = self._generate_why_it_matters(
            competitor_name, event, segment_match, matched_triggers
        )
        
        # Generate recommended action
        recommended_action = self._generate_action(matched_triggers, risk_level)
        
        # Get sources
        sources = update.get("sources", [])
        
        return {
            "type": "customer_risk",
            "company": competitor_name,
            "event": event,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "why_it_matters": why_it_matters,
            "recommended_action": recommended_action,
            "sources": sources,
        }

    def _analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any] | None:
        """Analyze a raw post for customer risk."""
        title = post.get("title", "").lower()
        summary = post.get("summary", "").lower()
        source = post.get("source", "")
        
        if not title:
            return None
        
        combined_text = f"{title} {summary}"
        
        # Check if it mentions a competitor
        competitor_name = None
        for competitor in self.KNOWN_COMPETITORS:
            if competitor in combined_text:
                competitor_name = competitor.title()
                break
        
        # Also check detected_competitor field
        if not competitor_name:
            competitor_name = post.get("detected_competitor", "")
            if competitor_name and competitor_name.lower() == "market_signal":
                return None
        
        if not competitor_name:
            return None
        
        # Check for threat triggers
        risk_score = 0
        matched_triggers = []
        
        for trigger, score in self.THREAT_TRIGGERS.items():
            if trigger in combined_text:
                risk_score += score
                matched_triggers.append(trigger)
        
        # Check for customer segment overlap
        segment_match = any(keyword in combined_text for keyword in self.SEGMENT_KEYWORDS)
        if segment_match:
            risk_score += 3
        
        # Source credibility
        if "news" in source.lower() or "techcrunch" in source.lower():
            risk_score += 2
        elif "reddit" in source.lower():
            risk_score += 1
        
        # Cap at 10
        risk_score = min(risk_score, 10)
        
        # Only return if score >= 4
        if risk_score < 4:
            return None
        
        # Determine risk level
        if risk_score >= 7:
            risk_level = "High"
        elif risk_score >= 4:
            risk_level = "Medium"
        else:
            return None
        
        # Extract event description
        event = self._extract_event(title, summary, matched_triggers)
        
        # Generate why it matters
        why_it_matters = self._generate_why_it_matters(
            competitor_name, event, segment_match, matched_triggers
        )
        
        # Generate recommended action
        recommended_action = self._generate_action(matched_triggers, risk_level)
        
        # Get source info
        sources = [{
            "source_name": post.get("source_label", source),
            "url": post.get("url", "#")
        }]
        
        return {
            "type": "customer_risk",
            "company": competitor_name,
            "event": event,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "why_it_matters": why_it_matters,
            "recommended_action": recommended_action,
            "sources": sources,
        }

    def _extract_event(self, title: str, description: str, triggers: List[str]) -> str:
        """Extract concise event description."""
        # Use title if it's concise
        if len(title.split()) <= 10:
            return title.strip().capitalize()
        
        # Try to extract key phrase based on triggers
        for trigger in triggers:
            if trigger in title:
                # Extract sentence containing trigger
                sentences = title.split(".")
                for sentence in sentences:
                    if trigger in sentence:
                        return sentence.strip().capitalize()
        
        # Fallback: first 10 words of title
        words = title.split()[:10]
        return " ".join(words).strip().capitalize()

    def _generate_why_it_matters(
        self, company: str, event: str, segment_match: bool, triggers: List[str]
    ) -> str:
        """Generate why this risk matters to Campus Cortex AI."""
        reasons = []
        
        # Segment overlap
        if segment_match:
            reasons.append("Targets our core K-12 segment")
        
        # Trigger-specific reasons
        if "free" in triggers or "price drop" in triggers or "discount" in triggers:
            reasons.append("Could trigger price competition")
        
        if "acquired" in triggers or "acquisition" in triggers:
            reasons.append("Consolidation may strengthen competitor position")
        
        if "partnership" in triggers:
            reasons.append("Expands their distribution reach")
        
        if "launched" in triggers or "new feature" in triggers:
            reasons.append("Feature parity threat")
        
        if "raised funding" in triggers:
            reasons.append("Increased competitive pressure expected")
        
        # Combine reasons
        if reasons:
            return ". ".join(reasons)
        
        return f"{company} action may impact customer retention"

    def _generate_action(self, triggers: List[str], risk_level: str) -> str:
        """Generate recommended action based on threat type."""
        if "free" in triggers or "price drop" in triggers or "discount" in triggers:
            return "Review pricing strategy and prepare retention offers"
        
        if "acquired" in triggers or "acquisition" in triggers:
            return "Monitor integration timeline and customer migration risk"
        
        if "partnership" in triggers:
            return "Evaluate partnership opportunities to counter distribution advantage"
        
        if "launched" in triggers or "new feature" in triggers:
            return "Assess feature gap and prioritize roadmap response"
        
        if "raised funding" in triggers:
            return "Prepare for increased competitive activity and marketing spend"
        
        if risk_level == "High":
            return "Immediate executive review required"
        
        return "Monitor closely and prepare contingency plan"

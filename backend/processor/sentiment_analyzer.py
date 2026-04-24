"""Sentiment scoring utilities based on TextBlob polarity."""

from typing import Any, Dict, List

from textblob import TextBlob


class SentimentAnalyzer:
    """Analyze overall and source-level sentiment from scraped posts."""

    SOURCE_KEYS = ["hackernews", "newsapi"]

    def _label_from_score(self, score: float) -> str:
        """Convert a polarity score into a sentiment label."""
        if score > 0.1:
            return "positive"
        if score < -0.1:
            return "negative"
        return "neutral"

    def default_sentiment(self) -> Dict[str, Any]:
        """Return a default neutral sentiment payload."""
        breakdown = {
            source: {"score": 0.0, "label": "neutral"}
            for source in self.SOURCE_KEYS
        }
        return {
            "overall_score": 0.0,
            "overall_label": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "total_analyzed": 0,
            "breakdown_by_source": breakdown,
        }

    def analyze_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run sentiment analysis across all scraped posts."""
        scores: List[float] = []
        source_scores: Dict[str, List[float]] = {source: [] for source in self.SOURCE_KEYS}

        for post in posts:
            try:
                text = f"{post.get('title', '')} {post.get('content', '')}".strip()
                analysis = TextBlob(text)
                polarity = float(analysis.sentiment.polarity)
                scores.append(polarity)

                source = post.get("source", "hackernews")
                if source in source_scores:
                    source_scores[source].append(polarity)
            except Exception:
                continue

        if not scores:
            return self.default_sentiment()

        avg = sum(scores) / len(scores)
        overall_label = self._label_from_score(avg)

        positive_count = len([score for score in scores if score > 0.1])
        negative_count = len([score for score in scores if score < -0.1])
        neutral_count = len(scores) - positive_count - negative_count

        breakdown_by_source: Dict[str, Dict[str, Any]] = {}
        for source, values in source_scores.items():
            if values:
                source_avg = sum(values) / len(values)
                source_label = self._label_from_score(source_avg)
            else:
                source_avg = 0.0
                source_label = "neutral"
            breakdown_by_source[source] = {
                "score": round(source_avg, 2),
                "label": source_label,
            }

        return {
            "overall_score": round(avg, 2),
            "overall_label": overall_label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_analyzed": len(scores),
            "breakdown_by_source": breakdown_by_source,
        }

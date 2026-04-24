"""NewsAPI headline scraper for global news trends."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

import config


class NewsApiScraper:
    """Fetch top headlines from NewsAPI and normalize records."""

    BASE_URL = "https://newsapi.org/v2/top-headlines"

    def _parse_timestamp(self, published_at: Optional[str]) -> int:
        """Convert RFC3339 timestamp to unix seconds."""
        if not published_at:
            return int(datetime.now().timestamp())

        try:
            normalized = published_at.replace("Z", "+00:00")
            return int(datetime.fromisoformat(normalized).timestamp())
        except ValueError:
            return int(datetime.now().timestamp())

    def scrape(self, categories: List[str], limit: int, country: str = "us") -> List[Dict[str, Any]]:
        """Fetch and dedupe headlines for the requested categories."""
        if not config.NEWSAPI_KEY:
            raise ValueError("NEWSAPI_KEY is missing")

        results: List[Dict[str, Any]] = []
        per_category = max(3, min(10, limit // max(1, len(categories)) + 2))

        for category in categories:
            try:
                response = requests.get(
                    self.BASE_URL,
                    params={
                        "apiKey": config.NEWSAPI_KEY,
                        "country": country,
                        "category": category,
                        "pageSize": per_category,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                payload = response.json()

                for article in payload.get("articles", []):
                    title = (article.get("title") or "").strip()
                    url = (article.get("url") or "").strip()
                    if not title or not url:
                        continue

                    source_name = (article.get("source") or {}).get("name") or "NewsAPI"
                    summary = (article.get("description") or "").strip()

                    results.append(
                        {
                            "title": title,
                            "content": summary,
                            "url": url,
                            "upvotes": 0,
                            "comments": 0,
                            "source": "newsapi",
                            "source_label": source_name,
                            "created_utc": self._parse_timestamp(article.get("publishedAt")),
                        }
                    )
            except Exception as exc:
                print(f"[NewsApiScraper] Category '{category}' failed: {exc}")
                continue

        unique: Dict[str, Dict[str, Any]] = {}
        seen_titles = set()
        for item in results:
            url_key = item["url"].strip().lower()
            title_key = item["title"].strip().lower()
            if url_key in unique or title_key in seen_titles:
                continue
            unique[url_key] = item
            seen_titles.add(title_key)

        deduped = list(unique.values())
        deduped.sort(key=lambda item: item.get("created_utc", 0), reverse=True)
        return deduped[:limit]

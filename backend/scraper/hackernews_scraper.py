"""Hacker News scraping via official Firebase API."""

import html
import re
import time
from typing import Any, Dict, List, Optional

import requests


class HackerNewsScraper:
    """Scrape top Hacker News stories and key discussion comments."""

    TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
    ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

    def _fetch_json(self, url: str) -> Any:
        """Fetch JSON payload with timeout and status checks."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    def _clean_comment_text(self, raw_text: str) -> str:
        """Strip HTML tags and collapse whitespace from comment text."""
        unescaped = html.unescape(raw_text or "")
        no_tags = re.sub(r"<[^>]+>", " ", unescaped)
        return re.sub(r"\s+", " ", no_tags).strip()

    def _extract_top_comments(self, story: Dict[str, Any], max_comments: int = 3) -> List[str]:
        """Fetch top-level comments for the story if available."""
        comment_ids = story.get("kids") or []
        comments: List[str] = []

        for comment_id in comment_ids[:max_comments]:
            try:
                comment = self._fetch_json(self.ITEM_URL.format(item_id=comment_id))
            except Exception:
                continue

            if not comment or comment.get("deleted") or comment.get("dead"):
                continue

            text = self._clean_comment_text(comment.get("text") or "")
            if text:
                comments.append(text[:240])

        return comments

    def scrape(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Scrape top HN stories and include comment context where available."""
        results: List[Dict[str, Any]] = []

        try:
            top_story_ids = self._fetch_json(self.TOP_STORIES_URL)
        except Exception as exc:
            print(f"[HackerNewsScraper] Failed to fetch top stories: {exc}")
            return results

        for story_id in top_story_ids[: max(30, limit * 2)]:
            if len(results) >= limit:
                break

            try:
                story = self._fetch_json(self.ITEM_URL.format(item_id=story_id))
            except Exception:
                continue

            if not story or story.get("type") != "story":
                continue

            title = (story.get("title") or "").strip()
            if not title:
                continue

            comments = self._extract_top_comments(story)
            comment_block = " | ".join(comments)
            url = story.get("url") or f"https://news.ycombinator.com/item?id={story_id}"

            results.append(
                {
                    "title": title,
                    "content": comment_block[:600],
                    "url": url,
                    "upvotes": story.get("score", 0) or 0,
                    "comments": story.get("descendants", 0) or 0,
                    "source": "hackernews",
                    "source_label": "Hacker News",
                    "created_utc": story.get("time", int(time.time())),
                }
            )

        unique_by_url: Dict[str, Dict[str, Any]] = {}
        for item in results:
            item_url = item.get("url")
            if item_url and item_url not in unique_by_url:
                unique_by_url[item_url] = item

        deduped = list(unique_by_url.values())
        deduped.sort(key=lambda item: item.get("upvotes", 0), reverse=True)
        return deduped[:limit]

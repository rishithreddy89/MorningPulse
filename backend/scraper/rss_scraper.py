"""RSS feed scraping utilities for EdTech sources."""

import time
from typing import Any, Dict, List

import feedparser
import requests


class RssScraper:
    """Scrape keyword-filtered stories from RSS feeds."""

    GOOGLE_NEWS_URL = (
        "https://news.google.com/rss/search"
        "?q=edtech%20OR%20education%20technology%20OR%20school%20software"
        "&hl=en-IN&gl=IN&ceid=IN:en"
    )

    EDSURGE_RSS_URLS = [
        "https://www.edsurge.com/feed",
        "https://edsurge.com/feed.rss",
        "https://www.edsurge.com/rss",
    ]
    EDSURGE_FALLBACK_URLS = [
        "https://thejournal.com/rss-feeds/all-articles.aspx",
        "https://dev.to/feed/tag/education",
        "https://dev.to/feed/tag/edtech",
    ]
    PRODUCTHUNT_RSS_URL = "https://www.producthunt.com/feed"
    REQUEST_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def fetch_google_news(self) -> List[Dict[str, Any]]:
        """Fetch EdTech-focused Google News RSS posts."""
        try:
            response = requests.get(self.GOOGLE_NEWS_URL, headers=self.REQUEST_HEADERS, timeout=10)
            feed = feedparser.parse(response.content)
        except Exception as exc:
            print(f"[RssScraper] Google News fetch error: {exc}")
            return []

        if not feed.entries:
            print(f"[RssScraper] Google News returned 0 entries. bozo={feed.bozo} status={getattr(feed, 'status', 'N/A')}")

        return [
            {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "source": "google_news",
                "source_label": "Google News",
                "url": entry.get("link", ""),
            }
            for entry in feed.entries
            if entry.get("title") and entry.get("link")
        ]

    def fetch_reddit_rss(self) -> List[Dict[str, Any]]:
        """Fetch posts from EdTech-relevant Reddit using Pullpush API."""
        posts: List[Dict[str, Any]] = []
        subreddits = ["edtech", "Teachers", "OnlineLearning"]
        
        for sub in subreddits:
            post_data = self._try_pullpush(sub)
            
            for post in post_data:
                title = post.get("title", "")
                permalink = post.get("permalink", "")
                if title and permalink:
                    posts.append(
                        {
                            "title": title,
                            "link": f"https://reddit.com{permalink}",
                            "summary": (post.get("selftext") or "")[:300],
                            "source": "reddit",
                            "source_label": "Reddit",
                            "url": f"https://reddit.com{permalink}",
                        }
                    )
        
        print(f"[Pipeline] Reddit RSS: {len(posts)} posts")
        return posts

    def _try_pullpush(self, subreddit: str) -> list:
        """Fallback: Pullpush Reddit archive API."""
        try:
            url = "https://api.pullpush.io/reddit/search/submission"
            params = {
                "subreddit": subreddit,
                "size": 10,
                "sort": "score",
                "sort_type": "desc"
            }
            response = requests.get(url, params=params, headers=self.REQUEST_HEADERS, timeout=10)
            print(f"[Reddit] Pullpush {subreddit} status: {response.status_code}")
            
            if not response.content or len(response.content) < 10:
                return []
            
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"[Reddit] Pullpush {subreddit} failed: {e}")
            return []

    def fetch_edsurge(self) -> List[Dict[str, Any]]:
        """Fetch EdTech posts from EdSurge RSS feed."""
        for url in self.EDSURGE_RSS_URLS:
            try:
                response = requests.get(url, headers=self.REQUEST_HEADERS, timeout=10)
                print(f"[EdSurge] Trying {url} → status: {response.status_code}")
                feed = feedparser.parse(response.content)
                print(f"[EdSurge] bozo: {feed.bozo}, entries: {len(feed.entries)}")
                
                if feed.entries:
                    posts = [
                        {
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", ""),
                            "source": "edsurge",
                            "source_label": "EdSurge",
                            "url": entry.get("link", ""),
                        }
                        for entry in feed.entries
                        if entry.get("title") and entry.get("link")
                    ]
                    print(f"[Pipeline] EdSurge: {len(posts)} posts")
                    return posts
            except Exception as exc:
                print(f"[EdSurge] Fetch error {url}: {exc}")
                continue
        
        print("[EdSurge] All primary URLs failed, trying fallback sources")
        return self._fetch_edsurge_fallback()

    def _fetch_edsurge_fallback(self) -> List[Dict[str, Any]]:
        """Fetch EdTech posts from fallback sources when EdSurge fails."""
        for url in self.EDSURGE_FALLBACK_URLS:
            try:
                response = requests.get(url, headers=self.REQUEST_HEADERS, timeout=10)
                print(f"[EdSurge Fallback] Trying {url} → status: {response.status_code}")
                feed = feedparser.parse(response.content)
                print(f"[EdSurge Fallback] bozo: {feed.bozo}, entries: {len(feed.entries)}")
                
                if feed.entries:
                    posts = [
                        {
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "summary": entry.get("summary", ""),
                            "source": "edsurge",
                            "source_label": "EdSurge",
                            "url": entry.get("link", ""),
                        }
                        for entry in feed.entries
                        if entry.get("title") and entry.get("link")
                    ]
                    print(f"[Pipeline] EdSurge: {len(posts)} posts")
                    return posts
            except Exception as exc:
                print(f"[EdSurge Fallback] Fetch error {url}: {exc}")
                continue
        
        print("[Pipeline] EdSurge: 0 posts")
        return []

    def fetch_producthunt(self) -> List[Dict[str, Any]]:
        """Fetch EdTech-related products from Product Hunt RSS feed."""
        try:
            response = requests.get(self.PRODUCTHUNT_RSS_URL, headers=self.REQUEST_HEADERS, timeout=10)
            feed = feedparser.parse(response.content)
        except Exception as exc:
            print(f"[RssScraper] Product Hunt fetch error: {exc}")
            return []

        posts: List[Dict[str, Any]] = []
        edtech_keywords = ["education", "learning", "student", "teacher", "edtech", "classroom", "school"]

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")

            if not title or not link:
                continue

            text = f"{title} {summary}".lower()

            # Filter only EdTech-related products
            if any(keyword in text for keyword in edtech_keywords):
                posts.append(
                    {
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "source": "producthunt",
                        "source_label": "Product Hunt",
                        "url": link,
                    }
                )
        return posts

    def _entry_timestamp(self, entry: Any) -> float:
        """Return a unix timestamp for the RSS entry publication time."""
        if entry.get("published_parsed"):
            return float(time.mktime(entry.published_parsed))
        return time.time()

    def _matches_keywords(self, title: str, summary: str, keywords: List[str]) -> bool:
        """Check whether the RSS entry title or summary contains configured keywords."""
        title_lower = (title or "").lower()
        summary_lower = (summary or "").lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower or keyword_lower in summary_lower:
                return True
        return False

    def scrape(self, feed_urls: List[str], keywords: List[str], hours_lookback: int) -> List[Dict[str, Any]]:
        """Scrape EdTech articles from RSS feeds."""
        results: List[Dict[str, Any]] = []
        cutoff = time.time() - (hours_lookback * 3600)

        for feed_url in feed_urls:
            try:
                feed = feedparser.parse(feed_url)
                feed_title = feed.feed.get("title", feed_url)

                for entry in feed.entries:
                    if entry.get("published_parsed"):
                        entry_time = time.mktime(entry.published_parsed)
                        if entry_time < cutoff:
                            continue

                    title = entry.get("title", "")
                    summary = (entry.get("summary") or "")[:600]

                    if not self._matches_keywords(title, summary, keywords):
                        continue

                    results.append(
                        {
                            "title": title,
                            "content": summary,
                            "url": entry.get("link", ""),
                            "upvotes": 0,
                            "comments": 0,
                            "source": "rss",
                            "source_label": feed_title,
                            "created_utc": self._entry_timestamp(entry),
                        }
                    )

                time.sleep(0.5)
            except Exception as exc:
                print(f"[RssScraper] RSS feed error {feed_url}: {exc}")
                continue

        results.sort(key=lambda item: item.get("created_utc", 0), reverse=True)
        return results

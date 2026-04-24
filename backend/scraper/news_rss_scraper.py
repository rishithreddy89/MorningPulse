"""RSS scraper for EdTech news sources - replaces broken Reddit."""

import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import feedparser


RSS_SOURCES = [
    {
        "name": "EdSurge",
        "url": "https://edsurge.com/feed",
        "category": "edtech"
    },
    {
        "name": "EdWeek",
        "url": "https://www.edweek.org/feed",
        "category": "education"
    },
    {
        "name": "eSchool News",
        "url": "https://www.eschoolnews.com/feed",
        "category": "edtech"
    },
    {
        "name": "THE Journal",
        "url": "https://thejournal.com/rss-feeds/all-articles.aspx",
        "category": "edtech"
    },
    {
        "name": "Google News EdTech",
        "url": "https://news.google.com/rss/search?q=edtech+school+management+software&hl=en-US&gl=US&ceid=US:en",
        "category": "news"
    },
    {
        "name": "Google News Teacher Tools",
        "url": "https://news.google.com/rss/search?q=teacher+tools+classroom+software&hl=en-US&gl=US&ceid=US:en",
        "category": "news"
    },
    {
        "name": "Google News LMS",
        "url": "https://news.google.com/rss/search?q=LMS+learning+management+system+school&hl=en-US&gl=US&ceid=US:en",
        "category": "news"
    }
]

KEYWORDS = [
    "edtech", "education technology", "school management",
    "teacher tools", "lms", "learning management", "classroom",
    "gradebook", "student information", "canvas", "schoology",
    "classdojo", "google classroom", "powerschool", "blackboard"
]


class NewsRssScraper:
    
    def __init__(self, hours_lookback: int = 48):
        self.hours_lookback = hours_lookback
        self.cutoff = datetime.utcnow() - timedelta(hours=hours_lookback)
    
    def scrape_all(self) -> List[Dict[str, Any]]:
        """Scrape all RSS sources and return filtered posts."""
        all_posts = []
        
        for source in RSS_SOURCES:
            try:
                posts = self._scrape_feed(source)
                all_posts.extend(posts)
                print(f"{source['name']}: {len(posts)} posts")
                time.sleep(0.5)
            except Exception as e:
                print(f"RSS error {source['name']}: {e}")
                continue
        
        # Deduplicate by URL
        seen_urls = set()
        unique = []
        for post in all_posts:
            url = post.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(post)
        
        print(f"RSS total: {len(unique)} unique posts")
        return unique
    
    def _scrape_feed(self, source: dict) -> List[Dict[str, Any]]:
        """Scrape a single RSS feed."""
        feed = feedparser.parse(source["url"])
        posts = []
        
        for entry in feed.entries:
            # Check publication date
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date < self.cutoff:
                    continue
            
            title = entry.get("title", "").strip()
            if not title:
                continue
            
            # Keyword filter for Google News feeds
            if source["category"] == "news":
                text = (title + " " + 
                        entry.get("summary", "")).lower()
                if not any(kw in text for kw in KEYWORDS):
                    continue
            
            summary = entry.get("summary", "")
            # Strip HTML tags from summary
            summary = re.sub(r'<[^>]+>', '', summary)[:500]
            
            posts.append({
                "title": title,
                "summary": summary,
                "url": entry.get("link", ""),
                "source": source["name"],
                "category": source["category"],
                "published": entry.get("published", "")
            })
        
        return posts

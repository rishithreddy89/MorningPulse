"""Reddit scraping utilities powered by PRAW."""

import time
from typing import Any, Dict, List

import praw

import config


class RedditScraper:
    """Scrape EdTech-relevant Reddit submissions."""

    def __init__(self) -> None:
        """Initialize an authenticated PRAW Reddit client."""
        self.reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent=config.REDDIT_USER_AGENT,
        )
        print("[RedditScraper] Reddit scraper initialized")

    def _matches_keywords(self, title: str, content: str, keywords: List[str]) -> bool:
        """Check whether title or content contains any configured keyword."""
        title_lower = (title or "").lower()
        content_lower = (content or "").lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower or keyword_lower in content_lower:
                return True
        return False

    def _format_post(self, post: Any, subreddit_name: str) -> Dict[str, Any]:
        """Map a PRAW submission into the backend's normalized post schema."""
        return {
            "title": post.title,
            "content": post.selftext[:600] if post.selftext else "",
            "url": f"https://reddit.com{post.permalink}",
            "upvotes": post.score,
            "comments": post.num_comments,
            "source": "reddit",
            "source_label": f"r/{subreddit_name}",
            "created_utc": post.created_utc,
        }

    def scrape(self, subreddits: List[str], keywords: List[str], hours_lookback: int) -> List[Dict[str, Any]]:
        """Scrape EdTech posts from Reddit subreddits."""
        results: List[Dict[str, Any]] = []
        cutoff_time = time.time() - (hours_lookback * 3600)

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                for post in subreddit.hot(limit=50):
                    if post.created_utc < cutoff_time:
                        continue
                    if not self._matches_keywords(post.title, post.selftext, keywords):
                        continue
                    results.append(self._format_post(post, subreddit_name))

                for post in subreddit.new(limit=30):
                    if post.created_utc < cutoff_time:
                        continue
                    if not self._matches_keywords(post.title, post.selftext, keywords):
                        continue
                    results.append(self._format_post(post, subreddit_name))

                time.sleep(1)
            except Exception as exc:
                print(f"[RedditScraper] Error scraping r/{subreddit_name}: {exc}")
                continue

        unique_by_url: Dict[str, Dict[str, Any]] = {}
        for item in results:
            url = item.get("url")
            if url and url not in unique_by_url:
                unique_by_url[url] = item

        deduped = list(unique_by_url.values())
        deduped.sort(key=lambda item: item.get("upvotes", 0), reverse=True)
        return deduped[: config.MAX_POSTS]

    def get_trending_keywords(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count keyword frequency across all post titles."""
        keyword_counts: Dict[str, int] = {keyword: 0 for keyword in config.KEYWORDS}

        for post in posts:
            title = (post.get("title", "") or "").lower()
            for keyword in config.KEYWORDS:
                keyword_counts[keyword] += title.count(keyword.lower())

        ranked = sorted(
            ((keyword, count) for keyword, count in keyword_counts.items() if count > 0),
            key=lambda item: item[1],
            reverse=True,
        )
        return dict(ranked[:15])

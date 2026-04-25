"""Intelligent post selection with diversity-based filtering for rich outputs."""

import re
from collections import Counter
from typing import Any, Dict, List

# ════════════════════════════════════════════════════════════════════════════
# DIVERSITY-BASED SELECTION LIMITS
# ════════════════════════════════════════════════════════════════════════════
MAX_RSS_NEWS = 10      # Max posts from RSS/news sources
MAX_REDDIT = 10        # Max posts from Reddit
MAX_HACKERNEWS = 10    # Max posts from HackerNews
MAX_PER_COMPETITOR = 3 # Max posts per competitor
MAX_PER_SOURCE = 5     # Max posts per individual source

# ════════════════════════════════════════════════════════════════════════════
# KEYWORD SCORING
# ════════════════════════════════════════════════════════════════════════════
HIGH_VALUE = [
    "edtech", "lms", "e-learning", "online learning", "classroom technology",
    "ai in education", "curriculum", "learning platform", "student information system"
]

MEDIUM_VALUE = [
    "teacher", "student", "education", "school", "grading", "classroom",
    "learning", "teaching", "academic", "university", "college"
]

NOISE_WORDS = ["arrested", "crime", "sports", "weather", "celebrity"]

# ════════════════════════════════════════════════════════════════════════════
# COMPETITOR DETECTION
# ════════════════════════════════════════════════════════════════════════════
COMPETITOR_NAMES = [
    "ClassDojo", "Google Classroom", "Canvas", "Schoology", "PowerSchool",
    "Blackboard", "Seesaw", "Edmodo", "Remind", "Moodle", "Brightspace",
    "D2L", "Instructure", "Anthology", "Ellucian", "Workday Student",
    "Khan Academy", "Coursera", "Udemy", "Duolingo", "Quizlet"
]


def extract_competitor(text: str) -> str:
    """Extract competitor name from text using keyword matching."""
    text_lower = text.lower()
    
    for competitor in COMPETITOR_NAMES:
        if competitor.lower() in text_lower:
            return competitor
    
    return "market_signal"  # Tag as market signal instead of dropping


def extract_keywords(posts: List[Dict[str, Any]]) -> Dict[str, int]:
    """Extract keyword frequencies for trend detection."""
    keywords = []
    
    for post in posts:
        title = post.get("title", "").lower()
        summary = post.get("summary", "").lower()
        text = f"{title} {summary}"
        
        # Extract meaningful words (3+ chars, not common words)
        words = re.findall(r'\b[a-z]{3,}\b', text)
        keywords.extend(words)
    
    # Count frequencies
    counter = Counter(keywords)
    
    # Filter out common words
    common_words = {"the", "and", "for", "with", "this", "that", "from", "have", "been", "will"}
    filtered = {k: v for k, v in counter.items() if k not in common_words and v >= 2}
    
    return dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:20])


def score_post(post: Dict[str, Any]) -> int:
    """Calculate relevance score for a post based on weighted keyword matching."""
    title = post.get("title", "").lower()
    summary = post.get("summary", "").lower()
    text = f"{title} {summary}"
    source = post.get("source", "")

    score = 0

    # Source priority boost
    if source == "edsurge":
        score += 3
    elif source == "producthunt":
        score += 2
    elif source in ["google_news", "news_rss"]:
        score += 1

    # High-value keyword scoring
    for keyword in HIGH_VALUE:
        if keyword in text:
            score += 3
            if keyword in title:
                score += 2

    # Medium-value keyword scoring
    for keyword in MEDIUM_VALUE:
        if keyword in text:
            score += 1
            if keyword in title:
                score += 1

    # Noise penalty
    for noise in NOISE_WORDS:
        if noise in text:
            score -= 3

    # Competitor detection bonus
    competitor = extract_competitor(text)
    if competitor != "market_signal":
        score += 2
        post["detected_competitor"] = competitor

    post["relevance_score"] = score
    return score


def select_diverse_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Select posts with diversity constraints to ensure rich outputs.
    
    Strategy:
    - Up to 10 posts from RSS/news sources
    - Up to 10 posts from Reddit
    - Up to 10 posts from HackerNews
    - Max 3 posts per competitor
    - Max 5 posts per individual source
    
    Target: 20-40 posts total
    """
    
    # Categorize posts by source type
    rss_news_posts = []
    reddit_posts = []
    hackernews_posts = []
    
    for post in posts:
        source = post.get("source", "").lower()
        
        if "reddit" in source:
            reddit_posts.append(post)
        elif "hackernews" in source or "hn" in source:
            hackernews_posts.append(post)
        else:
            # RSS, news, edsurge, producthunt, etc.
            rss_news_posts.append(post)
    
    # Sort each category by score
    rss_news_posts.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    reddit_posts.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    hackernews_posts.sort(key=lambda p: p.get("relevance_score", 0), reverse=True)
    
    # Select from each category with diversity constraints
    selected = []
    source_count = {}
    competitor_count = {}
    
    def add_post(post: Dict[str, Any]) -> bool:
        """Add post if it passes diversity constraints."""
        source = post.get("source", "unknown")
        competitor = post.get("detected_competitor", "market_signal")
        
        # Check source limit
        if source_count.get(source, 0) >= MAX_PER_SOURCE:
            return False
        
        # Check competitor limit (but allow unlimited market_signal posts)
        if competitor != "market_signal" and competitor_count.get(competitor, 0) >= MAX_PER_COMPETITOR:
            return False
        
        # Add post
        selected.append(post)
        source_count[source] = source_count.get(source, 0) + 1
        competitor_count[competitor] = competitor_count.get(competitor, 0) + 1
        return True
    
    # Add from RSS/news (up to 10)
    for post in rss_news_posts[:MAX_RSS_NEWS * 2]:  # Check more than limit
        if len([p for p in selected if p.get("source", "").lower() not in ["reddit", "hackernews"]]) >= MAX_RSS_NEWS:
            break
        add_post(post)
    
    # Add from Reddit (up to 10)
    for post in reddit_posts[:MAX_REDDIT * 2]:
        if len([p for p in selected if "reddit" in p.get("source", "").lower()]) >= MAX_REDDIT:
            break
        add_post(post)
    
    # Add from HackerNews (up to 10)
    for post in hackernews_posts[:MAX_HACKERNEWS * 2]:
        if len([p for p in selected if "hackernews" in p.get("source", "").lower()]) >= MAX_HACKERNEWS:
            break
        add_post(post)
    
    return selected


def select_best_posts(posts: List[Dict[str, Any]], n: int = 40) -> List[Dict[str, Any]]:
    """
    Select the best posts using diversity-based selection.
    
    Steps:
    1. Score all posts
    2. Normalize URLs
    3. Detect competitors
    4. Apply diversity selection (20-40 posts)
    5. Ensure source attribution
    6. Extract keyword frequencies
    """
    
    if not posts:
        return []

    print(f"\n{'='*70}")
    print(f"[PostSelector] DIVERSITY-BASED SELECTION STARTING")
    print(f"{'='*70}")
    print(f"[PostSelector] Total raw posts: {len(posts)}")

    # ════════════════════════════════════════════════════════════════════════
    # STEP 1: Score all posts and normalize URLs
    # ════════════════════════════════════════════════════════════════════════
    for post in posts:
        score_post(post)
        
        # Normalize URL field
        url = post.get("url") or post.get("link") or post.get("href") or ""
        if isinstance(url, str) and url.startswith("http"):
            post["url"] = url
        else:
            post["url"] = ""
        
        # Ensure source attribution
        if "source_label" not in post:
            post["source_label"] = post.get("source", "Unknown").title()

    # ════════════════════════════════════════════════════════════════════════
    # STEP 2: Relax filters - allow posts >= 40 characters
    # ════════════════════════════════════════════════════════════════════════
    valid_posts = []
    for post in posts:
        title = post.get("title", "")
        summary = post.get("summary", "")
        combined = f"{title} {summary}"
        
        # Relaxed filter: >= 40 chars
        if len(combined.strip()) >= 40:
            valid_posts.append(post)
    
    print(f"[PostSelector] Posts after length filter (>=40 chars): {len(valid_posts)}")

    # ════════════════════════════════════════════════════════════════════════
    # STEP 3: Apply diversity-based selection
    # ════════════════════════════════════════════════════════════════════════
    final_posts = select_diverse_posts(valid_posts)
    
    print(f"[PostSelector] Posts after diversity selection: {len(final_posts)}")

    # ════════════════════════════════════════════════════════════════════════
    # STEP 4: Debug logging
    # ════════════════════════════════════════════════════════════════════════
    sources = set(p.get("source", "unknown") for p in final_posts)
    competitors = set(p.get("detected_competitor", "market_signal") for p in final_posts)
    
    print(f"\n[PostSelector] DIVERSITY BREAKDOWN:")
    print(f"  Sources: {sources}")
    print(f"  Detected competitors: {competitors}")
    
    # Count by source type
    rss_count = len([p for p in final_posts if p.get("source", "").lower() not in ["reddit", "hackernews"]])
    reddit_count = len([p for p in final_posts if "reddit" in p.get("source", "").lower()])
    hn_count = len([p for p in final_posts if "hackernews" in p.get("source", "").lower()])
    
    print(f"  RSS/News: {rss_count}")
    print(f"  Reddit: {reddit_count}")
    print(f"  HackerNews: {hn_count}")
    
    # Count by competitor
    competitor_breakdown = {}
    for post in final_posts:
        comp = post.get("detected_competitor", "market_signal")
        competitor_breakdown[comp] = competitor_breakdown.get(comp, 0) + 1
    
    print(f"\n[PostSelector] COMPETITOR BREAKDOWN:")
    for comp, count in sorted(competitor_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"  {comp}: {count} posts")

    # ════════════════════════════════════════════════════════════════════════
    # STEP 5: Extract keyword frequencies for trend detection
    # ════════════════════════════════════════════════════════════════════════
    keywords = extract_keywords(final_posts)
    print(f"\n[PostSelector] TOP KEYWORDS (for trend detection):")
    for keyword, count in list(keywords.items())[:10]:
        print(f"  {keyword}: {count} mentions")

    # ════════════════════════════════════════════════════════════════════════
    # STEP 6: URL validation check
    # ════════════════════════════════════════════════════════════════════════
    valid_urls = sum(1 for p in final_posts if p.get("url"))
    print(f"\n[PostSelector] URL Coverage: {valid_urls}/{len(final_posts)} posts have URLs")
    
    if valid_urls < len(final_posts) * 0.5:
        print(f"[PostSelector] ⚠️  WARNING: Less than 50% of posts have URLs!")

    print(f"{'='*70}\n")

    return final_posts

"""Intelligent post selection with weighted scoring and diversity filtering."""

from typing import Any, Dict, List

TOP_N = 15  # Select top 15 most relevant posts
MAX_PER_SOURCE = 5  # Max posts per source for diversity

HIGH_VALUE = [
    "edtech",
    "lms",
    "e-learning",
    "online learning",
    "classroom technology",
    "ai in education",
    "curriculum",
]

MEDIUM_VALUE = [
    "teacher",
    "student",
    "education",
    "school",
    "grading",
    "learning platform",
]

NOISE_WORDS = ["arrested", "crime", "sports", "weather"]


def score_post(post: Dict[str, Any]) -> int:
    """Calculate relevance score for a post based on weighted keyword matching."""
    title = post.get("title", "").lower()
    summary = post.get("summary", "").lower()
    text = f"{title} {summary}"
    source = post.get("source", "")

    score = 0

    # Source priority boost
    if source == "edsurge":
        score += 3  # High trust EdTech source
    elif source == "producthunt":
        score += 2  # Useful for competitor tracking

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
                score += 2

    # Noise penalty
    for noise in NOISE_WORDS:
        if noise in text:
            score -= 2

    post["relevance_score"] = score
    return score


def select_diverse_posts(posts: List[Dict[str, Any]], n: int = 15, max_per_source: int = 5) -> List[Dict[str, Any]]:
    """Select top N posts with diversity constraint: max posts per source."""
    selected: List[Dict[str, Any]] = []
    source_count: Dict[str, int] = {}

    for post in posts:
        source = post.get("source", "unknown")

        if source_count.get(source, 0) < max_per_source:
            selected.append(post)
            source_count[source] = source_count.get(source, 0) + 1

        if len(selected) == n:
            break

    return selected


def select_best_posts(posts: List[Dict[str, Any]], n: int = TOP_N) -> List[Dict[str, Any]]:
    """
    Select the best N posts using weighted scoring, ranking, and diversity.

    Steps:
    1. Score all posts
    2. Normalize and validate URLs
    3. Rank by score
    4. Filter posts with score > 0
    5. Apply diversity selection (max 5 per source)
    6. Fallback to top N if insufficient quality posts
    7. Ensure all posts have source attribution fields
    """
    if not posts:
        return []

    print(f"[PostSelector] Total posts: {len(posts)}")

    # Score all posts and normalize URLs
    for post in posts:
        score_post(post)
        
        # CRITICAL: Normalize URL field - try multiple field names
        url = post.get("url") or post.get("link") or post.get("href") or ""
        
        # Validate URL
        if isinstance(url, str) and url.startswith("http"):
            post["url"] = url
        else:
            post["url"] = ""
        
        # Ensure source attribution fields exist
        if "source_label" not in post:
            post["source_label"] = post.get("source", "Unknown").title()

    # Rank by score
    ranked_posts = sorted(posts, key=lambda p: p.get("relevance_score", 0), reverse=True)

    # Filter quality posts (score > 0)
    quality_posts = [p for p in ranked_posts if p.get("relevance_score", 0) > 0]

    print(f"[PostSelector] Quality posts (score > 0): {len(quality_posts)}")

    # Apply diversity selection
    final_posts = select_diverse_posts(quality_posts, n=n, max_per_source=MAX_PER_SOURCE)

    # Fallback: if insufficient quality posts, use top N ranked
    if len(final_posts) < n:
        print(f"[PostSelector] Insufficient quality posts, using top {n} ranked")
        final_posts = ranked_posts[:n]

    # DEBUG: Check URL coverage
    print("\n===== DEBUG URL CHECK =====")
    valid_urls = 0
    for post in final_posts:
        if post.get("url"):
            valid_urls += 1
        else:
            print(f"❌ Missing URL: {post.get('title', 'Unknown')[:60]}")
    
    print(f"Valid URLs: {valid_urls}/{len(final_posts)}")
    print("===========================\n")

    print(f"[PostSelector] Selected posts: {len(final_posts)}")

    return final_posts

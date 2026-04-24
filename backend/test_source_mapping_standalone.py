#!/usr/bin/env python3
"""Standalone test to verify source mapping logic."""

# Simulate the fixed mapping logic
def build_title_url_map(posts):
    """Build a mapping of post titles to URLs."""
    title_url_map = {}
    source_label_url_map = {}
    
    print("[Source Mapping] Building title → URL map")
    for post in posts:
        title = str(post.get("title", "")).lower().strip()
        # FIX: Try both 'url' and 'link' fields
        url = post.get("url") or post.get("link") or ""
        source_label = str(post.get("source_label", "")).lower().strip()
        
        if title and url:
            title_url_map[title] = url
        if source_label and url:
            if source_label not in source_label_url_map:
                source_label_url_map[source_label] = url
    
    print(f"[Source Mapping] Mapped {len(title_url_map)} titles to URLs")
    
    # Debug: Show sample mappings
    if title_url_map:
        print("[Source Mapping] Sample mappings:")
        for title, url in list(title_url_map.items())[:5]:
            print(f"  {title[:60]}... → {url}")
    else:
        print("[Source Mapping] WARNING: No titles mapped! Check post structure.")
    
    return title_url_map, source_label_url_map


def map_source_url(source_name, title_url_map, source_label_url_map):
    """Map a source name to its URL."""
    if not source_name:
        return "#"
    
    source_lower = source_name.lower().strip()
    
    if source_lower in ["n/a", "unknown"]:
        return "#"
    
    # Try exact title match
    if source_lower in title_url_map:
        return title_url_map[source_lower]
    
    # Try source label match
    if source_lower in source_label_url_map:
        return source_label_url_map[source_lower]
    
    # Try fuzzy match on titles
    for title, url in title_url_map.items():
        if source_lower in title or title in source_lower:
            return url
    
    # Try fuzzy match on source labels
    for label, url in source_label_url_map.items():
        if source_lower in label or label in source_lower:
            return url
    
    return "#"


# Test data
test_posts = [
    {
        "title": "AI in Education: New Trends",
        "summary": "AI is transforming classrooms",
        "source": "edsurge",
        "source_label": "EdSurge",
        "url": "https://www.edsurge.com/news/ai-education",
    },
    {
        "title": "Teachers Struggle with EdTech",
        "summary": "Implementation challenges",
        "source": "reddit",
        "source_label": "Reddit",
        "link": "https://reddit.com/r/Teachers/post123",  # Using 'link' instead of 'url'
    },
    {
        "title": "New LMS Platform Launches",
        "summary": "Cloud-based learning system",
        "source": "hackernews",
        "source_label": "Hacker News",
        "url": "https://news.ycombinator.com/item?id=123",
    },
]

print("=" * 70)
print("SOURCE MAPPING FIX TEST")
print("=" * 70)
print()

# Build maps
title_map, label_map = build_title_url_map(test_posts)

print()
print("=" * 70)
print("TESTING URL MAPPING")
print("=" * 70)

test_cases = [
    ("AI in Education: New Trends", "Should match exact title"),
    ("Teachers Struggle with EdTech", "Should match title (from 'link' field)"),
    ("EdSurge", "Should match source label"),
    ("Reddit", "Should match source label"),
    ("Hacker News", "Should match source label"),
    ("education", "Should fuzzy match first title"),
    ("Unknown Source", "Should return '#' (no match)"),
]

for test_name, description in test_cases:
    url = map_source_url(test_name, title_map, label_map)
    status = "✅" if url and url != "#" else "❌"
    print(f"{status} {test_name:35} → {url:40} ({description})")

print()
print("=" * 70)
print("EXPECTED RESULTS:")
print("=" * 70)
print("✅ First 6 should have valid URLs")
print("❌ Last one should return '#' (no match)")
print()
print("KEY FIX: Using 'post.get(\"url\") or post.get(\"link\")' instead of just 'post.get(\"url\")'")
print("This handles both RSS feeds (which use 'link') and other scrapers (which use 'url')")
print("=" * 70)

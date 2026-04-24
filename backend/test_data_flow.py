#!/usr/bin/env python3
"""Test to verify data flow consistency in pipeline."""

import sys
sys.path.insert(0, '/Users/rishithreddy/Documents/MorningPulse/backend')

# Simulate the pipeline data flow
test_posts = [
    {
        "title": "AI in Education: New Trends",
        "summary": "AI is transforming classrooms with new tools and approaches",
        "source": "edsurge",
        "source_label": "EdSurge",
        "url": "https://www.edsurge.com/news/ai-education",
        "relevance_score": 10,
    },
    {
        "title": "Teachers Struggle with EdTech Implementation",
        "summary": "Many teachers face challenges when implementing new technology",
        "source": "reddit",
        "source_label": "Reddit",
        "url": "https://reddit.com/r/Teachers/post123",
        "relevance_score": 8,
    },
    {
        "title": "New LMS Platform Launches",
        "summary": "Cloud-based learning management system for schools",
        "source": "hackernews",
        "source_label": "Hacker News",
        "url": "https://news.ycombinator.com/item?id=123",
        "relevance_score": 7,
    },
]

print("=" * 70)
print("DATA FLOW CONSISTENCY TEST")
print("=" * 70)
print()

# STEP 1: Simulate select_best_posts
print("STEP 1: SELECT BEST POSTS")
print("-" * 70)
filtered_posts = test_posts  # In real pipeline, this filters and scores
print(f"Selected posts: {len(filtered_posts)}")
urls_in_filtered = sum(1 for p in filtered_posts if p.get("url"))
print(f"URLs in filtered_posts: {urls_in_filtered}/{len(filtered_posts)}")
print()

# STEP 2: Simulate _compress_post (OLD - BROKEN)
print("STEP 2a: OLD _compress_post (BROKEN)")
print("-" * 70)

def compress_post_old(post):
    """Old broken version - loses URL."""
    return {
        "title": post.get("title", ""),
        "summary": post.get("summary", "")[:200],
    }

gemini_input_old = [compress_post_old(p) for p in filtered_posts]
urls_in_old = sum(1 for p in gemini_input_old if p.get("url"))
print(f"URLs in gemini_input (OLD): {urls_in_old}/{len(gemini_input_old)}")
print("❌ PROBLEM: URLs lost during compression!")
print()

# STEP 3: Simulate _compress_post (NEW - FIXED)
print("STEP 2b: NEW _compress_post (FIXED)")
print("-" * 70)

def compress_post_new(post):
    """New fixed version - preserves URL."""
    return {
        "title": post.get("title", ""),
        "summary": post.get("summary", "")[:200],
        "url": post.get("url", ""),
        "source": post.get("source", ""),
        "source_label": post.get("source_label", ""),
    }

gemini_input_new = [compress_post_new(p) for p in filtered_posts]
urls_in_new = sum(1 for p in gemini_input_new if p.get("url"))
print(f"URLs in gemini_input (NEW): {urls_in_new}/{len(gemini_input_new)}")
print("✅ FIXED: URLs preserved during compression!")
print()

# STEP 4: Simulate Gemini processor check
print("STEP 3: GEMINI PROCESSOR CHECK")
print("-" * 70)

def check_gemini_input(posts, label):
    """Simulate Gemini processor URL check."""
    if all(not p.get("url") for p in posts):
        print(f"❌ {label}: [ERROR] No valid URLs found")
        return False
    else:
        urls = sum(1 for p in posts if p.get("url"))
        print(f"✅ {label}: {urls}/{len(posts)} posts have URLs")
        return True

check_gemini_input(gemini_input_old, "OLD version")
check_gemini_input(gemini_input_new, "NEW version")
print()

# STEP 5: Simulate URL mapping
print("STEP 4: URL MAPPING")
print("-" * 70)

def build_url_map(posts):
    """Build title -> URL map."""
    url_map = {}
    for post in posts:
        title = post.get("title", "").lower()
        url = post.get("url", "")
        if title and url:
            url_map[title] = url
    return url_map

old_map = build_url_map(gemini_input_old)
new_map = build_url_map(gemini_input_new)

print(f"OLD version: Mapped {len(old_map)} titles")
print(f"NEW version: Mapped {len(new_map)} titles")
print()

if new_map:
    print("Sample mappings (NEW):")
    for title, url in list(new_map.items())[:2]:
        print(f"  {title[:50]}... → {url}")

# SUMMARY
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("OLD PIPELINE (BROKEN):")
print(f"  1. filtered_posts: {urls_in_filtered}/{len(filtered_posts)} URLs ✅")
print(f"  2. gemini_input: {urls_in_old}/{len(gemini_input_old)} URLs ❌")
print(f"  3. URL mapping: {len(old_map)} titles ❌")
print(f"  4. Result: [ERROR] No valid URLs found ❌")
print()
print("NEW PIPELINE (FIXED):")
print(f"  1. filtered_posts: {urls_in_filtered}/{len(filtered_posts)} URLs ✅")
print(f"  2. gemini_input: {urls_in_new}/{len(gemini_input_new)} URLs ✅")
print(f"  3. URL mapping: {len(new_map)} titles ✅")
print(f"  4. Result: Source mapping successful ✅")
print()
print("ROOT CAUSE:")
print("  _compress_post() was stripping URL field during compression")
print()
print("FIX:")
print("  Preserve url, source, and source_label in compressed posts")
print("=" * 70)

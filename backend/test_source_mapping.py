#!/usr/bin/env python3
"""Test script to verify source mapping fix."""

import sys
sys.path.insert(0, '/Users/rishithreddy/Documents/MorningPulse/backend')

from processor.gemini_processor import GeminiProcessor

# Test data with both 'url' and 'link' fields
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

print("=" * 60)
print("SOURCE MAPPING TEST")
print("=" * 60)

processor = GeminiProcessor()
processor._input_posts = test_posts
processor._build_title_url_map(test_posts)

print("\n" + "=" * 60)
print("TESTING URL MAPPING")
print("=" * 60)

test_cases = [
    "AI in Education: New Trends",
    "Teachers Struggle with EdTech",
    "EdSurge",
    "Reddit",
    "Hacker News",
    "Unknown Source",
]

for test_name in test_cases:
    url = processor._map_source_url(test_name)
    status = "✅" if url and url != "#" else "❌"
    print(f"{status} {test_name[:40]:40} → {url}")

print("\n" + "=" * 60)
print("EXPECTED RESULTS:")
print("=" * 60)
print("✅ First 5 should have valid URLs")
print("❌ Last one should return '#' (no match)")
print("\nIf you see 0 titles mapped, the bug still exists!")
print("=" * 60)

#!/usr/bin/env python3
"""Test script to validate EdSurge RSS scraping."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scraper.rss_scraper import RssScraper

def test_edsurge():
    """Test EdSurge RSS feed scraping."""
    print("=" * 60)
    print("Testing EdSurge RSS Feed")
    print("=" * 60)
    
    scraper = RssScraper()
    posts = scraper.fetch_edsurge()
    
    print(f"\n[Result] EdSurge returned {len(posts)} posts")
    
    if posts:
        print("\n[Success] ✓ EdSurge scraping working!")
        print(f"\nShowing first 3 posts:")
        for i, post in enumerate(posts[:3], 1):
            print(f"\n  Post {i}:")
            print(f"    Title: {post.get('title', 'N/A')[:70]}...")
            print(f"    Link: {post.get('link', 'N/A')}")
            print(f"    Source: {post.get('source', 'N/A')}")
    else:
        print("\n[Warning] ✗ EdSurge returned 0 posts")
        print("Check the debug logs above for details")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_edsurge()

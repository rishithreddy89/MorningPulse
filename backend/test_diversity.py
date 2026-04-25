#!/usr/bin/env python3
"""Test script to verify diversity improvements in the pipeline."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from processor.post_selector import select_best_posts, extract_competitor, extract_keywords


def test_competitor_detection():
    """Test competitor detection."""
    print("\n" + "="*70)
    print("TEST 1: COMPETITOR DETECTION")
    print("="*70)
    
    test_cases = [
        ("ClassDojo launches new parent communication feature", "ClassDojo"),
        ("Google Classroom adds AI grading assistant", "Google Classroom"),
        ("Canvas LMS updates gradebook interface", "Canvas"),
        ("New EdTech startup raises $10M", "market_signal"),
        ("Teachers struggle with digital tool overload", "market_signal"),
    ]
    
    for text, expected in test_cases:
        result = extract_competitor(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:50]}...' → {result} (expected: {expected})")


def test_keyword_extraction():
    """Test keyword extraction."""
    print("\n" + "="*70)
    print("TEST 2: KEYWORD EXTRACTION")
    print("="*70)
    
    mock_posts = [
        {"title": "AI in education is transforming classrooms", "summary": "Artificial intelligence tools are helping teachers grade faster and provide personalized learning experiences."},
        {"title": "Privacy concerns grow in EdTech", "summary": "Schools are worried about student data privacy as more digital tools are adopted."},
        {"title": "AI-powered tutoring gains traction", "summary": "AI tutoring systems are becoming popular for personalized education."},
    ]
    
    keywords = extract_keywords(mock_posts)
    print(f"Extracted {len(keywords)} keywords:")
    for keyword, count in list(keywords.items())[:10]:
        print(f"  {keyword}: {count} mentions")


def test_diversity_selection():
    """Test diversity-based selection."""
    print("\n" + "="*70)
    print("TEST 3: DIVERSITY-BASED SELECTION")
    print("="*70)
    
    # Create mock posts from different sources
    mock_posts = []
    
    # HackerNews posts
    for i in range(15):
        mock_posts.append({
            "title": f"HN Post {i}: EdTech innovation in AI",
            "summary": "This is a HackerNews post about education technology and artificial intelligence in classrooms.",
            "source": "hackernews",
            "url": f"https://news.ycombinator.com/item?id={i}"
        })
    
    # Reddit posts
    for i in range(15):
        mock_posts.append({
            "title": f"Reddit Post {i}: Teachers discuss ClassDojo",
            "summary": "Teachers on Reddit are discussing their experiences with ClassDojo and other classroom management tools.",
            "source": "reddit",
            "url": f"https://reddit.com/r/teachers/{i}"
        })
    
    # RSS/News posts
    for i in range(20):
        competitor = ["ClassDojo", "Canvas", "Schoology", "PowerSchool", "Google Classroom"][i % 5]
        mock_posts.append({
            "title": f"News Post {i}: {competitor} announces new feature",
            "summary": f"{competitor} has announced a major update to their platform focusing on teacher productivity and student engagement.",
            "source": "edsurge",
            "url": f"https://edsurge.com/news/{i}"
        })
    
    print(f"Total mock posts: {len(mock_posts)}")
    
    # Run selection
    selected = select_best_posts(mock_posts, n=40)
    
    print(f"\n✅ Selected {len(selected)} posts")
    
    # Verify diversity
    sources = {}
    competitors = {}
    
    for post in selected:
        source = post.get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1
        
        comp = post.get("detected_competitor", "market_signal")
        competitors[comp] = competitors.get(comp, 0) + 1
    
    print(f"\nSource distribution:")
    for source, count in sources.items():
        print(f"  {source}: {count} posts")
    
    print(f"\nCompetitor distribution:")
    for comp, count in sorted(competitors.items(), key=lambda x: x[1], reverse=True):
        print(f"  {comp}: {count} posts")
    
    # Verify constraints
    print(f"\n{'='*70}")
    print("CONSTRAINT VERIFICATION:")
    print(f"{'='*70}")
    
    max_per_source = max(sources.values())
    print(f"Max posts per source: {max_per_source} (limit: 5) {'✅' if max_per_source <= 5 else '❌'}")
    
    max_per_competitor = max(competitors.values())
    print(f"Max posts per competitor: {max_per_competitor} (limit: 3) {'✅' if max_per_competitor <= 3 else '❌'}")
    
    hn_count = sources.get("hackernews", 0)
    print(f"HackerNews posts: {hn_count} (limit: 10) {'✅' if hn_count <= 10 else '❌'}")
    
    reddit_count = sources.get("reddit", 0)
    print(f"Reddit posts: {reddit_count} (limit: 10) {'✅' if reddit_count <= 10 else '❌'}")
    
    rss_count = sum(count for source, count in sources.items() if source not in ["hackernews", "reddit"])
    print(f"RSS/News posts: {rss_count} (limit: 10) {'✅' if rss_count <= 10 else '❌'}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("DIVERSITY PIPELINE IMPROVEMENTS - TEST SUITE")
    print("="*70)
    
    test_competitor_detection()
    test_keyword_extraction()
    test_diversity_selection()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

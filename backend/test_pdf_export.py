#!/usr/bin/env python3
"""Test script for PDF export functionality."""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from database.storage import Storage


def test_pdf_dependencies():
    """Check if PDF generation dependencies are available."""
    print("Testing PDF dependencies...")
    
    try:
        import weasyprint
        print("✓ weasyprint installed")
        return True
    except ImportError:
        print("✗ weasyprint not installed")
        try:
            import xhtml2pdf
            print("✓ xhtml2pdf installed (fallback)")
            return True
        except ImportError:
            print("✗ xhtml2pdf not installed (fallback)")
            print("\nInstall one of:")
            print("  pip install weasyprint")
            print("  pip install xhtml2pdf")
            return False


def test_smtp_config():
    """Check if SMTP is configured."""
    print("\nTesting SMTP configuration...")
    
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    
    if smtp_user and smtp_pass:
        print(f"✓ SMTP configured for {smtp_user}")
        return True
    else:
        print("✗ SMTP not configured")
        print("\nAdd to .env:")
        print("  SMTP_USER=your.email@gmail.com")
        print("  SMTP_PASS=xxxx-xxxx-xxxx-xxxx")
        return False


def test_digest_available():
    """Check if digest data is available."""
    print("\nTesting digest availability...")
    
    storage = Storage()
    digest = storage.get_today_digest()
    
    if digest:
        print(f"✓ Digest available for {digest.get('date')}")
        print(f"  - Trends: {len(digest.get('emerging_tech_trends', []))}")
        print(f"  - Competitors: {len(digest.get('competitor_updates', []))}")
        print(f"  - Pain points: {len(digest.get('user_pain_points', []))}")
        return True
    else:
        print("✗ No digest available")
        print("\nRun pipeline first:")
        print("  python main.py --run-now")
        return False


def test_template_exists():
    """Check if PDF template exists."""
    print("\nTesting PDF template...")
    
    template_path = os.path.join(os.path.dirname(__file__), "templates", "pdf_report.html")
    
    if os.path.exists(template_path):
        print(f"✓ Template exists at {template_path}")
        return True
    else:
        print(f"✗ Template not found at {template_path}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PDF Export Feature Test")
    print("=" * 60)
    
    results = [
        test_pdf_dependencies(),
        test_smtp_config(),
        test_digest_available(),
        test_template_exists(),
    ]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed! PDF export is ready.")
        print("\nNext steps:")
        print("  1. Start backend: python main.py")
        print("  2. Go to http://localhost:8080/settings")
        print("  3. Click 'Download PDF' or 'Send Now'")
    else:
        print("✗ Some tests failed. Fix issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

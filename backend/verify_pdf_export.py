#!/usr/bin/env python3
"""Quick verification script for PDF export feature files."""

import os
import sys


def check_file(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - NOT FOUND: {path}")
        return False


def check_content(path, search_text, description):
    """Check if file contains specific text."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            if search_text in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - text not found")
                return False
    except Exception as e:
        print(f"✗ {description} - error: {e}")
        return False


def main():
    """Run verification checks."""
    print("=" * 60)
    print("PDF Export Feature - File Verification")
    print("=" * 60)
    
    backend_dir = os.path.dirname(__file__)
    project_dir = os.path.dirname(backend_dir)
    
    results = []
    
    print("\n📦 Backend Files:")
    results.append(check_file(
        os.path.join(backend_dir, "api", "export_routes.py"),
        "Export routes module"
    ))
    results.append(check_file(
        os.path.join(backend_dir, "templates", "pdf_report.html"),
        "PDF template"
    ))
    results.append(check_content(
        os.path.join(backend_dir, "requirements.txt"),
        "weasyprint",
        "weasyprint in requirements.txt"
    ))
    results.append(check_content(
        os.path.join(backend_dir, "main.py"),
        "export_bp",
        "Export blueprint registered in main.py"
    ))
    
    print("\n🎨 Frontend Files:")
    frontend_dir = os.path.join(project_dir, "frontend", "src")
    results.append(check_file(
        os.path.join(frontend_dir, "routes", "settings.tsx"),
        "Settings page"
    ))
    results.append(check_content(
        os.path.join(frontend_dir, "routes", "settings.tsx"),
        "handleDownloadPDF",
        "Download PDF function in settings"
    ))
    results.append(check_content(
        os.path.join(frontend_dir, "routes", "settings.tsx"),
        "handleSendEmail",
        "Send email function in settings"
    ))
    
    print("\n📚 Documentation:")
    results.append(check_file(
        os.path.join(project_dir, "PDF_EXPORT_SETUP.md"),
        "Setup guide"
    ))
    results.append(check_file(
        os.path.join(project_dir, "PDF_EXPORT_CHECKLIST.md"),
        "Implementation checklist"
    ))
    
    print("\n⚙️  Configuration:")
    env_path = os.path.join(backend_dir, ".env")
    if os.path.exists(env_path):
        print(f"✓ .env file exists")
        with open(env_path, 'r') as f:
            env_content = f.read()
            if "SMTP_USER" in env_content:
                print("  ✓ SMTP_USER configured")
            else:
                print("  ⚠ SMTP_USER not configured (optional for email)")
            if "SMTP_PASS" in env_content:
                print("  ✓ SMTP_PASS configured")
            else:
                print("  ⚠ SMTP_PASS not configured (optional for email)")
    else:
        print(f"✓ .env file exists (create for email feature)")
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All core files verified!")
        print("\nNext steps:")
        print("  1. Install dependencies: cd backend && pip install -r requirements.txt")
        print("  2. Configure email (optional): Add SMTP_* to backend/.env")
        print("  3. Start backend: python main.py")
        print("  4. Test at: http://localhost:8080/settings")
    else:
        print("❌ Some files missing or incomplete")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

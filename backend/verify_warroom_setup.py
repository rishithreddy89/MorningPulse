#!/usr/bin/env python3
"""Verify War Room setup is correct."""

import os
import sys

def check_file_exists(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - NOT FOUND")
        return False

def check_file_contains(path, text, description):
    """Check if a file contains specific text."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            if text in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - TEXT NOT FOUND")
                return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False

def main():
    """Run all checks."""
    print("War Room Setup Verification")
    print("=" * 60)
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(backend_dir)
    
    checks = []
    
    # Backend files
    print("\nBackend Files:")
    checks.append(check_file_exists(
        os.path.join(backend_dir, "api", "warroom_routes.py"),
        "warroom_routes.py exists"
    ))
    
    checks.append(check_file_contains(
        os.path.join(backend_dir, "main.py"),
        "from api.warroom_routes import warroom_bp",
        "main.py imports warroom_bp"
    ))
    
    checks.append(check_file_contains(
        os.path.join(backend_dir, "main.py"),
        "app.register_blueprint(warroom_bp)",
        "main.py registers warroom_bp"
    ))
    
    # Frontend files
    print("\nFrontend Files:")
    checks.append(check_file_exists(
        os.path.join(project_dir, "frontend", "src", "components", "WarRoom.tsx"),
        "WarRoom.tsx exists"
    ))
    
    checks.append(check_file_exists(
        os.path.join(project_dir, "frontend", "src", "routes", "warroom.tsx"),
        "warroom route exists"
    ))
    
    checks.append(check_file_contains(
        os.path.join(project_dir, "frontend", "src", "components", "DashboardLayout.tsx"),
        "Launch War Room",
        "Dashboard has Launch War Room button"
    ))
    
    # Documentation
    print("\nDocumentation:")
    checks.append(check_file_exists(
        os.path.join(project_dir, "WAR_ROOM_DOCS.md"),
        "WAR_ROOM_DOCS.md exists"
    ))
    
    checks.append(check_file_exists(
        os.path.join(project_dir, "WAR_ROOM_QUICK_START.md"),
        "WAR_ROOM_QUICK_START.md exists"
    ))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✓ All checks passed ({passed}/{total})")
        print("\nNext steps:")
        print("1. Restart backend: cd backend && python3 main.py")
        print("2. Restart frontend: cd frontend && npm run dev")
        print("3. Open http://localhost:3000/warroom")
        return 0
    else:
        print(f"✗ Some checks failed ({passed}/{total})")
        print("\nPlease fix the issues above before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

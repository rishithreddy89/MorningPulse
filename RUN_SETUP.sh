#!/bin/bash
# LinkedIn Intelligence Feature - Complete Setup & Test Commands
# Copy and paste these commands in order

echo "════════════════════════════════════════════════════════════"
echo "LinkedIn Intelligence Feature - Setup & Test"
echo "════════════════════════════════════════════════════════════"
echo ""

# ============================================================
# STEP 1: Install Python Dependencies
# ============================================================
echo "📦 STEP 1: Installing Python dependencies..."
cd backend
pip install selenium webdriver-manager beautifulsoup4 lxml
echo "✅ Dependencies installed"
echo ""

# ============================================================
# STEP 2: Verify Imports
# ============================================================
echo "🔍 STEP 2: Verifying imports..."
python -c "
from scraper.linkedin_scraper import LinkedInScraper
from processor.linkedin_analyzer import LinkedInAnalyzer
from api.linkedin_routes import linkedin_bp
print('✅ All imports successful')
"
echo ""

# ============================================================
# STEP 3: Configuration Check
# ============================================================
echo "⚙️  STEP 3: Configuration check..."
echo ""
echo "Edit backend/.env and add these lines:"
echo "  LINKEDIN_EMAIL=your_linkedin_email_here"
echo "  LINKEDIN_PASSWORD=your_linkedin_password_here"
echo ""
echo "Press Enter when done..."
read

# ============================================================
# STEP 4: Database Setup
# ============================================================
echo "🗄️  STEP 4: Database setup..."
echo ""
echo "Run this SQL in Supabase SQL Editor:"
echo ""
echo "create table linkedin_intel ("
echo "  id uuid default gen_random_uuid() primary key,"
echo "  date text not null unique,"
echo "  content jsonb,"
echo "  created_at timestamp default now()"
echo ");"
echo ""
echo "Press Enter when done..."
read

# ============================================================
# STEP 5: Test Scraper (Optional - Watch It Work)
# ============================================================
echo "🧪 STEP 5: Test scraper (optional)..."
echo ""
echo "This will open a browser window and scrape LinkedIn."
echo "Skip this if you want to test via the UI instead."
echo ""
echo "Run test? (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    python -c "
from scraper.linkedin_scraper import LinkedInScraper
print('Starting scraper with visible browser...')
s = LinkedInScraper(headless=False)
posts = s.scrape_all()
print(f'✅ Scraped {len(posts)} posts')
if posts:
    print('Sample posts:')
    for post in posts[:3]:
        print(f'  - {post[\"competitor_name\"]}: {post[\"title\"][:60]}...')
"
fi
echo ""

# ============================================================
# STEP 6: Test Analyzer
# ============================================================
echo "🧪 STEP 6: Testing analyzer..."
python -c "
from processor.linkedin_analyzer import LinkedInAnalyzer
test_posts = [
    {
        'competitor_name': 'ClassDojo',
        'summary': 'Excited to announce our new AI-powered grading assistant.',
        'url': 'https://linkedin.com/test'
    }
]
result = LinkedInAnalyzer().analyze(test_posts)
print(f'✅ Analyzer working')
print(f'   Summary: {result[\"summary\"][:80]}...')
"
echo ""

# ============================================================
# STEP 7: Start Backend
# ============================================================
echo "🚀 STEP 7: Starting backend..."
echo ""
echo "Run this in a separate terminal:"
echo "  cd backend"
echo "  python main.py"
echo ""
echo "Press Enter when backend is running..."
read

# ============================================================
# STEP 8: Test API Endpoints
# ============================================================
echo "🧪 STEP 8: Testing API endpoints..."
echo ""

echo "Testing /api/linkedin/status..."
curl -s http://localhost:5000/api/linkedin/status | python -m json.tool
echo ""

echo "Testing /api/linkedin/scrape (triggers background job)..."
curl -s http://localhost:5000/api/linkedin/scrape | python -m json.tool
echo ""

echo "Note: Scrape takes 3-5 minutes. Check status with:"
echo "  curl http://localhost:5000/api/linkedin/status"
echo ""

# ============================================================
# STEP 9: Frontend Setup
# ============================================================
echo "🎨 STEP 9: Frontend setup..."
echo ""
echo "In a separate terminal, run:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open browser and:"
echo "  1. Click 'LinkedIn Intel' in sidebar"
echo "  2. Click 'Scrape LinkedIn' button"
echo "  3. Wait 3-5 minutes"
echo "  4. Page auto-refreshes with data"
echo ""

# ============================================================
# COMPLETE
# ============================================================
echo "════════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Quick Reference:"
echo ""
echo "Start Backend:"
echo "  cd backend && python main.py"
echo ""
echo "Start Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Test API:"
echo "  curl http://localhost:5000/api/linkedin/status"
echo "  curl http://localhost:5000/api/linkedin/scrape"
echo "  curl http://localhost:5000/api/linkedin/intel"
echo ""
echo "Test Scraper:"
echo "  cd backend"
echo "  python -c 'from scraper.linkedin_scraper import LinkedInScraper; s = LinkedInScraper(headless=False); posts = s.scrape_all(); print(f\"Got {len(posts)} posts\")'"
echo ""
echo "Documentation:"
echo "  LINKEDIN_FEATURE.md          - Full documentation"
echo "  LINKEDIN_IMPLEMENTATION.md   - Implementation details"
echo "  QUICKSTART_LINKEDIN.txt      - Quick reference"
echo "  VERIFICATION_CHECKLIST.md    - Testing checklist"
echo ""
echo "════════════════════════════════════════════════════════════"

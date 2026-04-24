#!/bin/bash

echo "=========================================="
echo "LinkedIn Intelligence Feature Setup"
echo "=========================================="
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install selenium webdriver-manager beautifulsoup4 lxml

echo ""
echo "✅ Dependencies installed"
echo ""

# Check environment variables
echo "🔍 Checking environment variables..."
if grep -q "LINKEDIN_EMAIL" .env && grep -q "LINKEDIN_PASSWORD" .env; then
    echo "✅ LinkedIn credentials found in .env"
else
    echo "⚠️  LinkedIn credentials NOT configured"
    echo "   Add these to backend/.env:"
    echo "   LINKEDIN_EMAIL=your_linkedin_email_here"
    echo "   LINKEDIN_PASSWORD=your_linkedin_password_here"
fi

echo ""
echo "🗄️  Database setup required:"
echo "   Run this SQL in Supabase:"
echo ""
echo "   create table linkedin_intel ("
echo "     id uuid default gen_random_uuid() primary key,"
echo "     date text not null unique,"
echo "     content jsonb,"
echo "     created_at timestamp default now()"
echo "   );"
echo ""

# Test imports
echo "🧪 Testing imports..."
python -c "
try:
    from scraper.linkedin_scraper import LinkedInScraper
    from processor.linkedin_analyzer import LinkedInAnalyzer
    from api.linkedin_routes import linkedin_bp
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure LinkedIn credentials in backend/.env"
echo "2. Run the database SQL in Supabase"
echo "3. Start backend: python main.py"
echo "4. Navigate to LinkedIn Intel in the dashboard"
echo "5. Click 'Scrape LinkedIn' button"
echo ""
echo "See LINKEDIN_FEATURE.md for full documentation"

#!/bin/bash

echo "=========================================="
echo "Scheduled Email Delivery — Quick Test"
echo "=========================================="
echo ""

# Check if Flask is running
if ! curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
    echo "❌ Flask is not running!"
    echo "   Start it with: cd backend && python main.py"
    exit 1
fi

echo "✅ Flask is running"
echo ""

# Test 1: Get current settings
echo "TEST 1: Current Settings"
echo "------------------------"
curl -s http://localhost:8080/api/settings | python3 -m json.tool
echo ""
echo ""

# Test 2: Check scheduler status
echo "TEST 2: Scheduler Status"
echo "------------------------"
curl -s http://localhost:8080/api/scheduler/status | python3 -m json.tool
echo ""
echo ""

# Test 3: Offer to trigger manual test
echo "TEST 3: Manual Pipeline Trigger"
echo "--------------------------------"
echo "This will:"
echo "  1. Run full pipeline (scrape + AI)"
echo "  2. Generate PDF"
echo "  3. Send email to configured address"
echo ""
read -p "Trigger manual test? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting pipeline..."
    curl -X POST http://localhost:8080/api/settings/test-pipeline
    echo ""
    echo ""
    echo "✅ Pipeline started!"
    echo ""
    echo "Watch Flask terminal for logs:"
    echo "  [Pipeline] Starting full pipeline..."
    echo "  [Pipeline] HackerNews: X posts"
    echo "  [Pipeline] Complete. Email sent to..."
    echo ""
    echo "Check email inbox in 2-3 minutes"
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Go to http://localhost:8080/settings"
echo "2. Change delivery time"
echo "3. Click Save changes"
echo "4. Verify scheduler updated:"
echo "   curl http://localhost:8080/api/scheduler/status"
echo ""
echo "To test scheduled delivery:"
echo "  - Set time to 2 minutes from now"
echo "  - Wait and check email"
echo "  - Change back to preferred time"
echo ""

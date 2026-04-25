#!/bin/bash

echo "=========================================="
echo "AI Solutions Feature — API Test"
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

echo "Testing /api/solutions endpoint..."
echo "-----------------------------------"
echo ""

# Test with sample pain point
curl -X POST http://localhost:8080/api/solutions \
  -H "Content-Type: application/json" \
  -d '{
    "pain_point": "Excessive digital tools causing stack bloat",
    "description": "Districts are struggling with too many tools and need consolidation",
    "source": "EdSurge"
  }' | python3 -m json.tool

echo ""
echo ""
echo "=========================================="
echo "Expected Response"
echo "=========================================="
echo ""
echo "Should see:"
echo "  - pain_point: (echoed back)"
echo "  - source: EdSurge"
echo "  - solutions: array of 4 objects"
echo ""
echo "Each solution should have:"
echo "  - title (string)"
echo "  - what (string)"
echo "  - how (string)"
echo "  - impact (string)"
echo "  - effort (low/medium/high)"
echo "  - priority (quick win/core feature/bold move)"
echo "  - target_user (admin/teacher/student/district)"
echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Go to http://localhost:8080"
echo "2. Scroll to 'User Pain Points' section"
echo "3. Click 'View solutions' on any pain point"
echo "4. Verify 4 solutions appear inline"
echo "5. Click 'Hide solutions' to collapse"
echo "6. Click 'Download as PDF report' to test export"
echo ""

#!/bin/bash

echo "=========================================="
echo "Restarting Flask Server"
echo "=========================================="
echo ""

# Kill existing Flask process
echo "Stopping existing Flask server..."
pkill -f "python.*main.py" || echo "No existing server found"
sleep 2

# Start Flask server
echo "Starting Flask server..."
cd /Users/rishithreddy/Documents/MorningPulse/backend

# Use the correct Python interpreter
/opt/homebrew/Cellar/python@3.14/3.14.4/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python main.py &

sleep 3

# Check if server is running
if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
    echo "✅ Flask server started successfully"
    echo ""
    echo "Server running at: http://localhost:8080"
    echo ""
    echo "Test endpoints:"
    echo "  curl http://localhost:8080/api/health"
    echo "  curl http://localhost:8080/api/digest"
    echo ""
else
    echo "❌ Flask server failed to start"
    echo "Check logs for errors"
fi

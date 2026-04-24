#!/bin/bash

echo "Testing Chat Endpoint"
echo "===================="
echo ""

# Test 1: Check if endpoint exists
echo "Test 1: Checking if endpoint is registered..."
curl -s -X OPTIONS http://localhost:5000/api/chat \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "Test 2: Sending chat request..."
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"message": "What are the trends?", "date": "2025-01-15"}' \
  | python -m json.tool

echo ""
echo "===================="
echo "If you see 405 METHOD NOT ALLOWED, restart the backend:"
echo "  cd backend && python main.py"

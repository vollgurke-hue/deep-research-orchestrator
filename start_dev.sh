#!/bin/bash

# Start both API Server and Vue frontend for development

echo "🚀 Starting Deep Research Orchestrator - Development Mode"
echo ""
echo "Starting services:"
echo "  - API Server (Port 5000) - Mock Mode"
echo "  - Vue Frontend (Port 5173)"
echo ""

# Kill any existing processes on these ports
fuser -k 5000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null
fuser -k 8002/tcp 2>/dev/null  # Kill old GUI if running

sleep 1

# Start API Server in background
echo "📡 Starting API Server (Mock Mode)..."
./viewer/venv/bin/python3 api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!

# Wait for API to start
sleep 2

# Check if API is running
if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "✓ API Server running (PID: $API_PID)"
else
    echo "❌ API Server failed to start. Check /tmp/api_server.log"
    exit 1
fi

# Start Vue frontend
echo "🎨 Starting Vue frontend..."
cd gui && npm run dev

# Cleanup on exit
trap "kill $API_PID 2>/dev/null; fuser -k 5000/tcp 2>/dev/null; fuser -k 5173/tcp 2>/dev/null" EXIT

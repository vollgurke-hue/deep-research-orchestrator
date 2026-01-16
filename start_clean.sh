#!/bin/bash
# Clean Start Script - Only API + Vue Frontend
# No old viewer system on port 8002

echo "============================================="
echo "🚀 Deep Research Orchestrator - Clean Start"
echo "============================================="
echo ""

# Kill old processes
echo "🧹 Cleaning up old processes..."
pkill -9 -f "serve_gui" 2>/dev/null
pkill -9 -f "start_gui" 2>/dev/null
fuser -k 8002/tcp 2>/dev/null
fuser -k 5000/tcp 2>/dev/null
sleep 1

# Start API Server (Port 5000)
echo "📡 Starting API Server (Port 5000, Mock Mode)..."
./viewer/venv/bin/python3 api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!
sleep 2

# Check API
if curl -s http://localhost:5000/api/status > /dev/null 2>&1; then
    echo "✓ API Server running (PID: $API_PID)"
else
    echo "❌ API Server failed to start. Check /tmp/api_server.log"
    exit 1
fi

# Start Vue Frontend (Port 5173)
echo "🎨 Starting Vue Frontend (Port 5173)..."
cd gui
npm run dev > /tmp/vue_frontend.log 2>&1 &
VUE_PID=$!
cd ..
sleep 3

# Check Vue
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✓ Vue Frontend running (PID: $VUE_PID)"
else
    echo "❌ Vue Frontend failed to start. Check /tmp/vue_frontend.log"
    exit 1
fi

echo ""
echo "============================================="
echo "✅ System Ready!"
echo "============================================="
echo ""
echo "📡 API Server:     http://localhost:5000"
echo "🎨 Vue Frontend:   http://localhost:5173"
echo ""
echo "📋 Logs:"
echo "   API:   tail -f /tmp/api_server.log"
echo "   Vue:   tail -f /tmp/vue_frontend.log"
echo ""
echo "🛑 To stop:"
echo "   pkill -f api_server.py"
echo "   pkill -f 'npm run dev'"
echo ""
echo "✓ Mock Mode ACTIVE - No llama-server needed"
echo "============================================="

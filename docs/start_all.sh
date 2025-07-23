#!/bin/bash
# Start all services for Multi-Agent Mission System

echo "🚀 Starting Multi-Agent Mission System..."
echo "===================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn app:app"
pkill -f "uvicorn mock_claude:app"
pkill -f "uvicorn mock_gemini:app"
sleep 2

# Activate virtual environment
source venv/bin/activate

# Start Hub
echo "🚀 Starting Hub..."
cd hub
uvicorn app:app --port 8000 --reload > ../logs/hub.log 2>&1 &
HUB_PID=$!
cd ..

# Start Claude Agent
echo "🚀 Starting Claude Agent..."
cd agent-claude
uvicorn mock_claude:app --port 8001 --reload > ../logs/claude.log 2>&1 &
CLAUDE_PID=$!
cd ..

# Start Gemini Agent
echo "🚀 Starting Gemini Agent..."
cd agent-gemini
uvicorn mock_gemini:app --port 8002 --reload > ../logs/gemini.log 2>&1 &
GEMINI_PID=$!
cd ..

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check services
echo ""
echo "🔍 Checking services status..."

if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Hub is running (PID: $HUB_PID)"
else
    echo "❌ Hub failed to start"
fi

if curl -s http://localhost:8001/docs > /dev/null; then
    echo "✅ Claude Agent is running (PID: $CLAUDE_PID)"
else
    echo "❌ Claude Agent failed to start"
fi

if curl -s http://localhost:8002/docs > /dev/null; then
    echo "✅ Gemini Agent is running (PID: $GEMINI_PID)"
else
    echo "❌ Gemini Agent failed to start"
fi

echo ""
echo "===================================="
echo "Services are running. Press Ctrl+C to stop all."
echo ""
echo "📝 Logs:"
echo "  - Hub: logs/hub.log"
echo "  - Claude: logs/claude.log"
echo "  - Gemini: logs/gemini.log"
echo ""
echo "🧪 To run tests:"
echo "  - python test_system.py"
echo "  - python test_integration.py"
echo "  - python test_error_cases.py"

# Wait for Ctrl+C
trap 'echo ""; echo "🛑 Stopping all services..."; kill $HUB_PID $CLAUDE_PID $GEMINI_PID; exit' INT
wait
#!/bin/bash
# Simple startup script for testing

echo "🚀 Starting Multi-Agent System (Simple Mode)"
echo "==========================================="

# Activate virtual environment
source venv/bin/activate

# Start only the Hub for testing
echo "Starting Hub server..."
python -m uvicorn hub.app:app --port 8000 --host 0.0.0.0 &
HUB_PID=$!

echo "Hub PID: $HUB_PID"
echo ""
echo "Hub running at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Stop with: kill $HUB_PID"
echo ""
echo "Waiting for Hub to start..."
sleep 5

# Test if Hub is running
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Hub is running!"
else
    echo "❌ Hub failed to start"
fi
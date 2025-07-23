#!/bin/bash
# Stop all services

echo "🛑 Stopping Multi-Agent Mission System..."
echo "===================================="

# Function to stop a service
stop_service() {
    local name=$1
    local pid_file="logs/$name.pid"
    
    if [ -f $pid_file ]; then
        pid=$(cat $pid_file)
        if ps -p $pid > /dev/null; then
            echo "🛑 Stopping $name (PID: $pid)..."
            kill $pid
            rm $pid_file
            echo "   ✅ $name stopped"
        else
            echo "   ⚠️  $name not running (stale PID file)"
            rm $pid_file
        fi
    else
        echo "   ⚠️  $name PID file not found"
    fi
}

# Stop all services
stop_service "Hub"
stop_service "Claude_Agent"
stop_service "Gemini_Agent"

# Kill any remaining uvicorn processes
echo ""
echo "🧹 Cleaning up any remaining processes..."
pkill -f "uvicorn hub.app:app" 2>/dev/null || true
pkill -f "claude_agent.py" 2>/dev/null || true
pkill -f "gemini_agent.py" 2>/dev/null || true

echo ""
echo "✅ All services stopped"
echo ""
echo "📝 Logs are preserved in: logs/"
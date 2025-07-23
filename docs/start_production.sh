#!/bin/bash
# Production startup script for Multi-Agent Mission System

set -e  # Exit on error

echo "🚀 Starting Multi-Agent Mission System (Production Mode)"
echo "=================================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️  No .env file found. Using defaults."
fi

# Create necessary directories
mkdir -p logs
mkdir -p hub/missions
mkdir -p ${AGENT_WORKSPACE_ROOT:-/tmp/agent-workspaces}

# Check Python environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check CLI tools
echo ""
echo "🔍 Checking CLI tools..."

if command -v ${CLAUDE_CLI_PATH:-claude} &> /dev/null; then
    echo "✅ Claude CLI found"
else
    echo "⚠️  Claude CLI not found. Agent will fail if used."
fi

if command -v ${GEMINI_CLI_PATH:-gemini} &> /dev/null; then
    echo "✅ Gemini CLI found"
else
    echo "⚠️  Gemini CLI not found. Agent will fail if used."
fi

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local log_file=$3
    
    echo "🚀 Starting $name..."
    nohup $command > $log_file 2>&1 &
    local pid=$!
    echo $pid > "logs/$name.pid"
    echo "   PID: $pid"
    sleep 2
    
    # Check if process is still running
    if ps -p $pid > /dev/null; then
        echo "   ✅ $name started successfully"
    else
        echo "   ❌ $name failed to start. Check $log_file"
        exit 1
    fi
}

# Start Hub
start_service "Hub" \
    "python -m uvicorn hub.app:app --host ${HUB_HOST:-0.0.0.0} --port ${HUB_PORT:-8000}" \
    "logs/hub.log"

# Start Claude Agent
start_service "Claude_Agent" \
    "python agent-claude/claude_agent.py" \
    "logs/claude-agent.log"

# Start Gemini Agent
start_service "Gemini_Agent" \
    "python agent-gemini/gemini_agent.py" \
    "logs/gemini-agent.log"

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Health check
echo ""
echo "🏥 Running health checks..."

check_service() {
    local name=$1
    local url=$2
    
    if curl -s $url/health > /dev/null; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name health check failed"
    fi
}

check_service "Hub" "http://localhost:${HUB_PORT:-8000}"
check_service "Claude Agent" "http://localhost:${CLAUDE_AGENT_PORT:-8001}"
check_service "Gemini Agent" "http://localhost:${GEMINI_AGENT_PORT:-8002}"

echo ""
echo "=================================================="
echo "✅ System is running!"
echo ""
echo "📊 Dashboard: http://localhost:${HUB_PORT:-8000}/docs"
echo "📝 Logs: tail -f logs/*.log"
echo "🛑 Stop: ./stop_production.sh"
echo ""
echo "📌 Quick Test:"
echo "   curl -X POST http://localhost:${HUB_PORT:-8000}/api/mission/register \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"workflow\": [{\"from\": \"start\", \"to\": \"claude\"}, {\"from\": \"claude\", \"to\": \"end\"}], \"mission\": \"Test mission\"}'"
echo ""
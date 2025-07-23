# LangGraph Multi-Agent Mission System

## Overview

A multi-agent orchestration system using LangGraph to coordinate Claude and Gemini CLI agents through HTTP APIs.

## Architecture

```
┌─────────┐     ┌──────────────┐     ┌─────────────┐
│ Client  │────▶│     Hub      │────▶│   Agents    │
│         │     │ (LangGraph)  │     │(Claude/Gemini)│
└─────────┘     └──────────────┘     └─────────────┘
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install CLI tools:
- Claude CLI: Follow official installation guide
- Gemini CLI: Follow official installation guide

3. Start services:
```bash
# Start Hub
cd hub && uvicorn app:app --reload --port 8000

# Start Claude Agent
cd agent-claude && uvicorn run_claude:app --reload --port 8001

# Start Gemini Agent
cd agent-gemini && uvicorn run_gemini:app --reload --port 8002
```

Or use Docker:
```bash
docker-compose up
```

## Usage

### 1. Register Mission
```bash
curl -X POST http://localhost:8000/api/mission/register \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": [
      {"from": "start", "to": "claude"},
      {"from": "claude", "to": "gemini"},
      {"from": "gemini", "to": "end"}
    ],
    "mission": "Analyze log.txt and summarize errors"
  }'
```

### 2. Get Mission Graph
```bash
curl http://localhost:8000/api/mission/{mission_id}/graph
```

### 3. Run Mission
```bash
curl -X POST http://localhost:8000/api/mission/{mission_id}/run
```

### 4. Check Status
```bash
curl http://localhost:8000/api/mission/{mission_id}/status
```

## Example

Run the example script:
```bash
python example_usage.py
```

## API Endpoints

### Hub
- `POST /api/mission/register` - Register new mission
- `GET /api/mission/{id}/graph` - Get workflow visualization
- `POST /api/mission/{id}/run` - Execute mission
- `GET /api/mission/{id}/status` - Check mission status

### Agents
- `POST /api/agent/command` - Receive command from Hub
- `POST /api/agent/result` - Send result to Hub (called by agents)

## Directory Structure
```
/hub/                 # LangGraph controller
├── app.py           # FastAPI server
├── flow_template.py # Workflow generator
└── missions/        # Mission storage

/agent-claude/        # Claude agent
├── run_claude.py    # Agent server
├── mission.md       # Current mission
└── result.md        # Execution result

/agent-gemini/        # Gemini agent
├── run_gemini.py    # Agent server
├── mission.md       # Current mission
└── result.md        # Execution result
```
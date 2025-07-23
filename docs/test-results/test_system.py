#!/usr/bin/env python3
"""
System test script for Multi-Agent Mission System
"""

import subprocess
import time
import requests
import json
import sys
import os
import signal
from datetime import datetime

# Configuration
HUB_URL = "http://localhost:8000"
CLAUDE_URL = "http://localhost:8001"
GEMINI_URL = "http://localhost:8002"

# Process storage
processes = []

def cleanup():
    """Clean up all processes"""
    print("\n🧹 Cleaning up processes...")
    for p in processes:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except:
            pass

def start_service(name, command, cwd):
    """Start a service in background"""
    print(f"🚀 Starting {name}...")
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid,
        env=env
    )
    processes.append(proc)
    return proc

def wait_for_service(url, name, timeout=30):
    """Wait for a service to be ready"""
    print(f"⏳ Waiting for {name} to be ready...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/docs")
            if response.status_code == 200:
                print(f"✅ {name} is ready!")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    
    print(f"❌ {name} failed to start within {timeout} seconds")
    return False

def test_hub_health():
    """Test Hub API health"""
    print("\n📋 Testing Hub API...")
    try:
        response = requests.get(f"{HUB_URL}/docs")
        assert response.status_code == 200
        print("✅ Hub API is healthy")
        return True
    except Exception as e:
        print(f"❌ Hub API test failed: {e}")
        return False

def test_mission_registration():
    """Test mission registration"""
    print("\n📝 Testing mission registration...")
    
    workflow = [
        {"from": "start", "to": "claude"},
        {"from": "claude", "to": "gemini"},
        {"from": "gemini", "to": "end"}
    ]
    
    mission_data = {
        "workflow": workflow,
        "mission": "Test mission: analyze this text and summarize it"
    }
    
    try:
        response = requests.post(f"{HUB_URL}/api/mission/register", json=mission_data)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        assert response.status_code == 200
        result = response.json()
        assert "missionId" in result
        assert result["status"] == "registered"
        print(f"✅ Mission registered successfully: {result['missionId']}")
        return result["missionId"]
    except Exception as e:
        print(f"❌ Mission registration failed: {e}")
        if 'response' in locals():
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None

def test_mission_graph(mission_id):
    """Test mission graph retrieval"""
    print(f"\n📊 Testing mission graph for {mission_id}...")
    
    try:
        response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/graph")
        assert response.status_code == 200
        result = response.json()
        assert "mermaid" in result
        print("✅ Mission graph retrieved successfully")
        print(f"📈 Graph:\n{result['mermaid']}")
        return True
    except Exception as e:
        print(f"❌ Mission graph test failed: {e}")
        return False

def test_mission_status(mission_id):
    """Test mission status check"""
    print(f"\n📍 Testing mission status for {mission_id}...")
    
    try:
        response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/status")
        assert response.status_code == 200
        result = response.json()
        print(f"✅ Mission status: {json.dumps(result, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Mission status test failed: {e}")
        return False

def create_mock_agents():
    """Create mock agent endpoints for testing"""
    print("\n🤖 Creating mock agent endpoints...")
    
    # Create mock Claude agent
    with open("agent-claude/mock_claude.py", "w") as f:
        f.write('''from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI(title="Mock Claude Agent")

class AgentCommandRequest(BaseModel):
    missionId: str
    agent: str
    mission: str

@app.post("/api/agent/command")
async def receive_command(request: AgentCommandRequest):
    print(f"Mock Claude received: {request.mission}")
    
    # Simulate processing
    await asyncio.sleep(2)
    
    # Send result back
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8000/api/agent/result",
            json={
                "missionId": request.missionId,
                "agent": "claude",
                "status": "success",
                "message": "Mock Claude completed processing",
                "result_path": "/tmp/claude_result.md"
            }
        )
    
    return {"status": "success"}
''')
    
    # Create mock Gemini agent
    with open("agent-gemini/mock_gemini.py", "w") as f:
        f.write('''from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI(title="Mock Gemini Agent")

class AgentCommandRequest(BaseModel):
    missionId: str
    agent: str
    mission: str

@app.post("/api/agent/command")
async def receive_command(request: AgentCommandRequest):
    print(f"Mock Gemini received: {request.mission}")
    
    # Simulate processing
    await asyncio.sleep(2)
    
    # Send result back
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8000/api/agent/result",
            json={
                "missionId": request.missionId,
                "agent": "gemini",
                "status": "success",
                "message": "Mock Gemini completed processing",
                "result_path": "/tmp/gemini_result.md"
            }
        )
    
    return {"status": "success"}
''')

def run_tests():
    """Run all tests"""
    print("🧪 Starting Multi-Agent Mission System Tests")
    print("=" * 50)
    
    try:
        # Create mock agents
        create_mock_agents()
        
        # Start services
        print("\n🔧 Starting services...")
        
        # Start Hub
        hub_proc = start_service(
            "Hub",
            "python -m uvicorn app:app --port 8000",
            "hub"
        )
        
        # Start mock agents
        claude_proc = start_service(
            "Claude Agent",
            "python -m uvicorn mock_claude:app --port 8001",
            "agent-claude"
        )
        
        gemini_proc = start_service(
            "Gemini Agent", 
            "python -m uvicorn mock_gemini:app --port 8002",
            "agent-gemini"
        )
        
        # Wait for services
        if not wait_for_service(HUB_URL, "Hub"):
            return False
        if not wait_for_service(CLAUDE_URL, "Claude Agent"):
            return False
        if not wait_for_service(GEMINI_URL, "Gemini Agent"):
            return False
        
        # Run tests
        print("\n🧪 Running tests...")
        
        # Test 1: Hub health
        if not test_hub_health():
            return False
        
        # Test 2: Mission registration
        mission_id = test_mission_registration()
        if not mission_id:
            return False
        
        # Test 3: Mission graph
        if not test_mission_graph(mission_id):
            return False
        
        # Test 4: Mission status
        if not test_mission_status(mission_id):
            return False
        
        # Test 5: Run mission (mock)
        print(f"\n🏃 Testing mission execution for {mission_id}...")
        try:
            response = requests.post(f"{HUB_URL}/api/mission/{mission_id}/run")
            assert response.status_code == 200
            print("✅ Mission started successfully")
            
            # Wait for completion
            print("⏳ Waiting for mission to complete...")
            for i in range(10):
                time.sleep(2)
                response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/status")
                status = response.json()
                print(f"   Status: {status['status']}, Current: {status.get('current_agent', 'N/A')}")
                
                if status["status"] in ["completed", "failed"]:
                    if status["status"] == "completed":
                        print("✅ Mission completed successfully!")
                    else:
                        print("❌ Mission failed!")
                    break
        except Exception as e:
            print(f"❌ Mission execution test failed: {e}")
            return False
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    finally:
        cleanup()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Integration test for Multi-Agent Mission System
Tests the complete workflow from registration to execution
"""

import subprocess
import time
import requests
import json
import os
import signal
from datetime import datetime

def test_full_workflow():
    """Test complete workflow"""
    HUB_URL = "http://localhost:8000"
    
    print("🔸 Integration Test: Complete Workflow")
    print("=" * 50)
    
    # 1. Register mission
    print("\n1️⃣ Registering mission...")
    workflow = [
        {"from": "start", "to": "claude"},
        {"from": "claude", "to": "gemini"},
        {"from": "gemini", "to": "end"}
    ]
    
    response = requests.post(f"{HUB_URL}/api/mission/register", json={
        "workflow": workflow,
        "mission": "Analyze system logs and provide recommendations"
    })
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.status_code}")
        return False
    
    result = response.json()
    mission_id = result["missionId"]
    print(f"✅ Mission registered: {mission_id}")
    
    # 2. Get visualization
    print("\n2️⃣ Getting workflow visualization...")
    response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/graph")
    if response.status_code == 200:
        graph = response.json()["mermaid"]
        print("✅ Workflow graph retrieved:")
        print(graph)
    else:
        print(f"❌ Failed to get graph: {response.status_code}")
        return False
    
    # 3. Check initial status
    print("\n3️⃣ Checking initial status...")
    response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/status")
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Initial status: {status['status']}")
        print(f"   Current agent: {status['current_agent']}")
    else:
        print(f"❌ Failed to get status: {response.status_code}")
        return False
    
    # 4. Execute mission
    print("\n4️⃣ Executing mission...")
    response = requests.post(f"{HUB_URL}/api/mission/{mission_id}/run")
    if response.status_code == 200:
        print("✅ Mission execution started")
    else:
        print(f"❌ Failed to start execution: {response.status_code}")
        return False
    
    # 5. Monitor progress
    print("\n5️⃣ Monitoring mission progress...")
    max_attempts = 20
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(2)
        response = requests.get(f"{HUB_URL}/api/mission/{mission_id}/status")
        
        if response.status_code == 200:
            status = response.json()
            current_status = status["status"]
            current_agent = status.get("current_agent", "N/A")
            
            print(f"   [{datetime.now().strftime('%H:%M:%S')}] Status: {current_status}, Agent: {current_agent}")
            
            if current_status == "completed":
                print("\n✅ Mission completed successfully!")
                print("\n📊 Final Results:")
                for agent, result in status.get("results", {}).items():
                    print(f"   - {agent}: {result.get('status', 'N/A')}")
                    if result.get('message'):
                        print(f"     Message: {result['message']}")
                return True
            
            elif current_status == "failed":
                print("\n❌ Mission failed!")
                return False
        
        attempt += 1
    
    print("\n❌ Mission timed out!")
    return False

def main():
    """Main test runner"""
    print("🧪 Multi-Agent Mission System - Integration Test")
    print("📅 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Check if services are running
    print("🔍 Checking services...")
    services_ok = True
    
    try:
        response = requests.get("http://localhost:8000/docs")
        print("✅ Hub is running")
    except:
        print("❌ Hub is not running")
        services_ok = False
    
    try:
        response = requests.get("http://localhost:8001/docs")
        print("✅ Claude Agent is running")
    except:
        print("❌ Claude Agent is not running")
        services_ok = False
    
    try:
        response = requests.get("http://localhost:8002/docs")
        print("✅ Gemini Agent is running")
    except:
        print("❌ Gemini Agent is not running")
        services_ok = False
    
    if not services_ok:
        print("\n⚠️  Please start all services first:")
        print("   1. cd hub && uvicorn app:app --port 8000")
        print("   2. cd agent-claude && uvicorn mock_claude:app --port 8001")
        print("   3. cd agent-gemini && uvicorn mock_gemini:app --port 8002")
        return False
    
    # Run integration test
    print()
    return test_full_workflow()

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ Integration test PASSED!")
    else:
        print("❌ Integration test FAILED!")
    exit(0 if success else 1)
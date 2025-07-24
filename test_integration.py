#!/usr/bin/env python3
"""
Full Integration Test: Hub -> Claude Agent -> Claude CLI -> Callback to Hub
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime
import time

async def test_full_integration():
    """Test complete workflow with Hub"""
    print("🧪 Full System Integration Test")
    print("=" * 60)
    
    hub_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 1: Register a mission
        print("\n1️⃣ Registering mission with Hub...")
        mission_request = {
            "workflow": [
                {"from": "start", "to": "claude"},
                {"from": "claude", "to": "end"}
            ],
            "mission": """Python 함수 최적화를 수행해주세요:

```python
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates
```

다음을 포함해주세요:
1. 시간 복잡도 분석
2. 최적화된 코드 (O(n) 복잡도)
3. 테스트 케이스
"""
        }
        
        try:
            response = await client.post(
                f"{hub_url}/api/mission/register",
                json=mission_request
            )
            
            if response.status_code == 200:
                result = response.json()
                mission_id = result["missionId"]
                print(f"✅ Mission registered: {mission_id}")
            else:
                print(f"❌ Failed to register mission: {response.status_code}")
                print(response.text)
                return
                
        except httpx.ConnectError:
            print("❌ Hub is not running. Please start it first.")
            print("   Run: cd hub && python3 app.py")
            return
        
        # Step 2: Run the mission
        print(f"\n2️⃣ Running mission {mission_id}...")
        response = await client.post(f"{hub_url}/api/mission/{mission_id}/run")
        
        if response.status_code == 200:
            print("✅ Mission execution started")
        else:
            print(f"❌ Failed to run mission: {response.status_code}")
            return
        
        # Step 3: Monitor mission status
        print("\n3️⃣ Monitoring mission progress...")
        max_wait = 120  # seconds
        check_interval = 5
        elapsed = 0
        
        while elapsed < max_wait:
            response = await client.get(f"{hub_url}/api/mission/{mission_id}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data["status"]
                current_agent = status_data.get("current_agent", "")
                results = status_data.get("results", {})
                
                print(f"\r⏳ Status: {status} | Agent: {current_agent} | Results: {list(results.keys())}", end="")
                
                if status in ["completed", "failed"]:
                    print(f"\n✅ Mission {status}!")
                    break
                    
                # Check if Claude has reported results
                if "claude" in results:
                    print(f"\n✅ Claude has reported results!")
                    break
                    
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        # Step 4: Get mission results
        print("\n\n4️⃣ Fetching mission results...")
        response = await client.get(f"{hub_url}/api/mission/{mission_id}/results")
        
        if response.status_code == 200:
            results_data = response.json()
            print(f"Mission Status: {results_data['status']}")
            
            for agent, result in results_data.get("results", {}).items():
                print(f"\n📊 {agent.upper()} Agent Results:")
                print(f"   Status: {result['status']}")
                print(f"   Message: {result['message']}")
                print(f"   Timestamp: {result['timestamp']}")
                
                # Print content preview
                content = result.get('content', '')
                if content and content != "No content available":
                    print(f"\n   📖 Content Preview:")
                    print("-" * 60)
                    print(content[:800] + "..." if len(content) > 800 else content)
                    print("-" * 60)
        
        # Step 5: Get mission history
        print("\n\n5️⃣ Mission History:")
        response = await client.get(f"{hub_url}/api/mission/{mission_id}/history")
        
        if response.status_code == 200:
            history = response.json()
            print(f"Created: {history['mission']['created_at']}")
            print(f"Status: {history['mission']['status']}")
            
            if history.get('executions'):
                print("\nAgent Executions:")
                for exec in history['executions']:
                    print(f"  - {exec['agent']}: {exec['status']} ({exec['start_time']})")
            
            if history.get('logs'):
                print("\nRecent Logs:")
                for log in history['logs'][-5:]:  # Last 5 logs
                    print(f"  [{log.get('level', 'INFO')}] {log.get('source', 'Unknown')}: {log.get('message', '')}")

async def check_services():
    """Check if all services are running"""
    print("🔍 Checking services...")
    
    services = [
        ("Hub", "http://localhost:8000/docs"),
        ("Claude Agent", "http://localhost:8001/health")
    ]
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    print(f"✅ {name} is running")
                else:
                    print(f"❌ {name} returned {response.status_code}")
            except:
                print(f"❌ {name} is not running")
    
    print()

if __name__ == "__main__":
    print("🚀 LangGraph Multi-Agent System Integration Test")
    print("=" * 60)
    
    # Check services first
    asyncio.run(check_services())
    
    # Run integration test
    asyncio.run(test_full_integration())
#!/usr/bin/env python3
"""
Full system test with Claude agent and Hub integration
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime

async def test_full_system():
    """Test the complete workflow: Hub -> Claude Agent -> CLI -> Result"""
    print("🧪 Full System Integration Test")
    print("=" * 60)
    
    # Test configuration
    hub_url = "http://localhost:8000"
    claude_agent_url = "http://localhost:8001"
    
    # Test mission
    mission_data = {
        "missionId": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent": "claude",
        "mission": """다음 Python 코드를 분석하고 개선점을 제시해주세요:

```python
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price'] * item['quantity']
    return total

# 사용 예시
items = [
    {'name': 'apple', 'price': 1000, 'quantity': 3},
    {'name': 'banana', 'price': 500, 'quantity': 5}
]
print(calculate_total(items))
```

다음 관점에서 분석해주세요:
1. 코드 품질 및 가독성
2. 에러 처리
3. 성능 최적화
4. 타입 힌트 추가
5. 문서화 개선
"""
    }
    
    print(f"📋 Mission ID: {mission_data['missionId']}")
    print(f"🤖 Target Agent: {mission_data['agent']}")
    print(f"📝 Mission: {mission_data['mission'][:100]}...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Step 1: Check if Claude agent is running
            print("\n1️⃣ Checking Claude agent status...")
            try:
                health_response = await client.get(f"{claude_agent_url}/health")
                if health_response.status_code == 200:
                    print("✅ Claude agent is running")
                else:
                    print("❌ Claude agent health check failed")
                    return
            except httpx.ConnectError:
                print("❌ Claude agent is not running. Please start it first.")
                print("   Run: cd agent-claude && python3 claude_agent.py")
                return
            
            # Step 2: Send mission to Claude agent
            print("\n2️⃣ Sending mission to Claude agent...")
            response = await client.post(
                f"{claude_agent_url}/api/agent/command",
                json=mission_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Agent response: {result}")
            else:
                print(f"❌ Agent returned error: {response.status_code}")
                print(f"   Response: {response.text}")
                return
            
            # Step 3: Check workspace for results
            print("\n3️⃣ Checking workspace for results...")
            workspace_path = Path("/tmp/claude-workspace") / mission_data['missionId']
            
            if workspace_path.exists():
                print(f"📁 Workspace found: {workspace_path}")
                
                # List all files
                print("\n📄 Files in workspace:")
                for file in workspace_path.iterdir():
                    print(f"  - {file.name} ({file.stat().st_size} bytes)")
                
                # Check key files
                mission_file = workspace_path / "mission.md"
                agent_info_file = workspace_path / "agentInfo.md"
                result_file = workspace_path / "result.md"
                
                if mission_file.exists():
                    print("\n✅ mission.md exists")
                    
                if agent_info_file.exists():
                    print("✅ agentInfo.md exists")
                    content = agent_info_file.read_text()
                    print(f"   Content preview: {content[:200]}...")
                    
                if result_file.exists():
                    print("\n✅ result.md created by Claude!")
                    content = result_file.read_text()
                    print(f"\n📖 Result content ({len(content)} chars):")
                    print("-" * 60)
                    print(content[:1500] + "..." if len(content) > 1500 else content)
                    print("-" * 60)
                else:
                    print("❌ result.md not found")
                    
                # Check agent result file
                agent_result_file = workspace_path / "claude_result.md"
                if agent_result_file.exists():
                    print("\n✅ Agent result file exists")
                    
            else:
                print(f"❌ Workspace not found: {workspace_path}")
                
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

async def test_parallel_missions():
    """Test multiple missions in parallel"""
    print("\n\n🚀 Testing Parallel Mission Execution")
    print("=" * 60)
    
    missions = [
        {
            "missionId": f"parallel_test_1_{datetime.now().strftime('%H%M%S')}",
            "agent": "claude",
            "mission": "Python에서 리스트의 중복 요소를 제거하는 3가지 방법을 보여주세요."
        },
        {
            "missionId": f"parallel_test_2_{datetime.now().strftime('%H%M%S')}",
            "agent": "claude",
            "mission": "JavaScript에서 Promise와 async/await의 차이점을 설명해주세요."
        },
        {
            "missionId": f"parallel_test_3_{datetime.now().strftime('%H%M%S')}",
            "agent": "claude",
            "mission": "SQL에서 JOIN의 종류(INNER, LEFT, RIGHT, FULL)를 예시와 함께 설명해주세요."
        }
    ]
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Send all missions in parallel
        tasks = []
        for mission in missions:
            print(f"📤 Sending mission: {mission['missionId']}")
            task = client.post(
                "http://localhost:8001/api/agent/command",
                json=mission
            )
            tasks.append(task)
        
        # Wait for all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        print("\n📊 Results:")
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"  ❌ Mission {i+1}: Error - {response}")
            elif response.status_code == 200:
                print(f"  ✅ Mission {i+1}: Success")
            else:
                print(f"  ❌ Mission {i+1}: HTTP {response.status_code}")

if __name__ == "__main__":
    print("🔧 Claude Agent Full System Test")
    print("=" * 60)
    print("Prerequisites:")
    print("  1. Claude CLI is installed and configured")
    print("  2. Claude agent is running on port 8001")
    print("  3. Hub is running on port 8000 (optional)")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_full_system())
    
    # Optional: Test parallel execution
    # asyncio.run(test_parallel_missions())
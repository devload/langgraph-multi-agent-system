#!/usr/bin/env python3
"""
Final comprehensive test of Claude agent system
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime
import time

async def test_claude_agent_final():
    """Final test with detailed monitoring"""
    print("🧪 Claude Agent Final Test")
    print("=" * 60)
    
    # Prepare test data
    mission_id = f"final_test_{datetime.now().strftime('%H%M%S')}"
    mission_data = {
        "missionId": mission_id,
        "agent": "claude", 
        "mission": """Python 코드 리뷰를 수행해주세요:

```python
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] % 2 == 0:
            result.append(data[i] * 2)
    return result
```

다음을 포함해서 분석해주세요:
1. 개선된 코드 버전
2. 성능 최적화 팁
3. Python 스타일 가이드 준수 여부
"""
    }
    
    print(f"📋 Mission ID: {mission_id}")
    print(f"📝 Mission: {mission_data['mission'][:80]}...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Send mission
        print("\n1️⃣ Sending mission to Claude agent...")
        start_time = time.time()
        
        response = await client.post(
            "http://localhost:8001/api/agent/command",
            json=mission_data
        )
        
        if response.status_code == 200:
            print("✅ Mission accepted")
        else:
            print(f"❌ Error: {response.status_code}")
            return
            
        # Monitor workspace
        workspace = Path(f"/tmp/claude-workspace/{mission_id}")
        print(f"\n2️⃣ Monitoring workspace: {workspace}")
        
        # Wait for Claude to process (with timeout)
        max_wait = 60  # seconds
        check_interval = 2  # seconds
        elapsed = 0
        
        while elapsed < max_wait:
            if workspace.exists():
                files = list(workspace.iterdir())
                print(f"\r⏳ Waiting... {elapsed}s | Files: {[f.name for f in files]}", end="")
                
                # Check if result.md exists
                result_file = workspace / "result.md"
                if result_file.exists():
                    print(f"\n✅ result.md created after {elapsed}s!")
                    break
                    
            time.sleep(check_interval)
            elapsed += check_interval
            
        total_time = time.time() - start_time
        print(f"\n⏱️ Total execution time: {total_time:.1f}s")
        
        # Display results
        print("\n3️⃣ Final Results:")
        print("-" * 60)
        
        if workspace.exists():
            for file in sorted(workspace.iterdir()):
                print(f"\n📄 {file.name} ({file.stat().st_size} bytes):")
                if file.suffix == ".md":
                    content = file.read_text()
                    if len(content) > 500:
                        print(content[:500] + "...")
                    else:
                        print(content)
                print("-" * 60)
        else:
            print("❌ Workspace not found")

# Simple sync test function
def test_direct_claude_call():
    """Direct test of Claude CLI"""
    print("\n\n🔧 Direct Claude CLI Test")
    print("=" * 60)
    
    import subprocess
    workspace = Path("/tmp/claude-direct-test")
    workspace.mkdir(exist_ok=True)
    
    # Create test files
    (workspace / "mission.md").write_text("# Test\n\nWrite a hello world function in Python")
    (workspace / "agentInfo.md").write_text("agentCallbackUrl: http://localhost:8000")
    
    # Run Claude
    cmd = [
        "claude", "--print", "--dangerously-skip-permissions",
        "-p", "mission.md 파일을 읽고, 처리한 뒤에 결과를 result.md에 저장하고 agentInfo.md의 agentCallbackUrl을 호출해주세요."
    ]
    
    print(f"Running: {' '.join(cmd[:3])}...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(workspace), timeout=30)
    
    print(f"Return code: {result.returncode}")
    print(f"Output: {result.stdout[:200]}...")
    
    # Check result
    result_file = workspace / "result.md"
    if result_file.exists():
        print(f"\n✅ result.md created!")
        print(result_file.read_text()[:300])
    else:
        print("\n❌ result.md not created")

if __name__ == "__main__":
    print("🚀 Claude Agent System Final Test")
    print("=" * 60)
    
    # Test 1: Through agent
    asyncio.run(test_claude_agent_final())
    
    # Test 2: Direct CLI
    test_direct_claude_call()
#!/usr/bin/env python3
"""
Direct test without Hub orchestration
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_direct_agent_call():
    """Test calling Claude agent directly"""
    print("🧪 Direct Claude Agent Test")
    print("=" * 60)
    
    # Test data
    mission_id = f"direct_test_{datetime.now().strftime('%H%M%S')}"
    mission_data = {
        "missionId": mission_id,
        "agent": "claude",
        "mission": "간단한 Hello World 함수를 Python으로 작성해주세요."
    }
    
    print(f"📋 Mission ID: {mission_id}")
    print(f"📝 Mission: {mission_data['mission']}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Send directly to Claude agent
        print("\n1️⃣ Sending mission to Claude agent...")
        try:
            response = await client.post(
                "http://localhost:8001/api/agent/command",
                json=mission_data
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                print("✅ Mission sent successfully")
            else:
                print("❌ Failed to send mission")
                return
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Wait a bit for processing
        print("\n2️⃣ Waiting for processing...")
        await asyncio.sleep(30)
        
        # Check workspace
        print("\n3️⃣ Checking results...")
        workspace = f"/tmp/claude-workspace/{mission_id}"
        
        import os
        if os.path.exists(workspace):
            print(f"✅ Workspace exists: {workspace}")
            
            for file in os.listdir(workspace):
                file_path = os.path.join(workspace, file)
                print(f"\n📄 {file}:")
                if file.endswith('.md'):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print(f"❌ Workspace not found: {workspace}")

if __name__ == "__main__":
    asyncio.run(test_direct_agent_call())
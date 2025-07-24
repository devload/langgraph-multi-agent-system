#!/usr/bin/env python3
"""
Test Claude CLI integration with the new mission.md and agentInfo.md approach
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_base import AgentCommandRequest
from agent_claude.claude_agent import ClaudeAgent
from pathlib import Path
import tempfile
import shutil

async def test_claude_cli():
    """Test Claude agent with actual CLI"""
    print("🧪 Testing Claude CLI Integration")
    print("=" * 50)
    
    # Create Claude agent
    config_path = Path(__file__).parent / "agent-claude" / "agent_config.yaml"
    agent = ClaudeAgent(str(config_path))
    
    # Create test request
    test_request = AgentCommandRequest(
        missionId="test_001",
        agent="claude",
        mission="간단한 Python 함수를 작성해주세요. 두 숫자를 받아서 더하는 add(a, b) 함수를 만들어주세요."
    )
    
    print(f"📋 Mission ID: {test_request.missionId}")
    print(f"🤖 Agent: {test_request.agent}")
    print(f"📝 Mission: {test_request.mission}")
    print("\nExecuting Claude CLI...")
    
    try:
        # Handle command directly
        result = await agent.handle_command(test_request)
        print(f"\n✅ Execution Result: {result}")
        
        # Check created files
        workspace_dir = agent.workspace_dir / test_request.missionId
        print(f"\n📁 Workspace: {workspace_dir}")
        
        if workspace_dir.exists():
            print("\n📄 Files created:")
            for file in workspace_dir.iterdir():
                print(f"  - {file.name}")
                if file.name == "result.md" and file.exists():
                    print(f"\n📖 Result content preview:")
                    content = file.read_text()
                    print(content[:500] + "..." if len(content) > 500 else content)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_claude_cli())
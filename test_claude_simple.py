#!/usr/bin/env python3
"""
Simple test for Claude CLI execution
"""

import subprocess
import tempfile
from pathlib import Path
import os

def test_claude_cli_simple():
    """Test Claude CLI with mission.md and agentInfo.md approach"""
    print("🧪 Testing Claude CLI with mission.md and agentInfo.md")
    print("=" * 50)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        print(f"📁 Workspace: {workspace}")
        
        # Create mission.md
        mission_file = workspace / "mission.md"
        mission_content = """# Mission

## Task
간단한 Python 함수를 작성해주세요. 두 숫자를 받아서 더하는 add(a, b) 함수를 만들어주세요.

## Instructions:
- Analyze the provided information carefully
- Provide clear and structured output
- If you create any files, save them in the current directory
- Include code examples where appropriate
"""
        mission_file.write_text(mission_content)
        print("📝 Created mission.md")
        
        # Create agentInfo.md
        agent_info_file = workspace / "agentInfo.md"
        agent_info_content = """# Agent Information

## Callback Details
agentCallbackUrl: http://localhost:8000/api/agent/result
missionId: test_001
agent: claude

## Instructions
- After processing the mission, save your results to result.md
- Make a POST request to the agentCallbackUrl with the following JSON:
  ```json
  {
    "missionId": "test_001",
    "agent": "claude",
    "status": "completed",
    "message": "Analysis completed successfully"
  }
  ```
"""
        agent_info_file.write_text(agent_info_content)
        print("📋 Created agentInfo.md")
        
        # Build Claude command
        cmd = [
            "claude",
            "-p", "mission.md 파일을 읽고, 처리한 뒤에 결과를 result.md에 저장하고 agentInfo.md의 agentCallbackUrl을 호출해주세요."
        ]
        
        print(f"\n🚀 Executing: {' '.join(cmd)}")
        print(f"📂 Working directory: {workspace}")
        
        try:
            # Execute Claude CLI
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(workspace),
                timeout=30
            )
            
            print(f"\n✅ Return code: {result.returncode}")
            
            if result.stdout:
                print("\n📤 STDOUT:")
                print(result.stdout)
            
            if result.stderr:
                print("\n📥 STDERR:")
                print(result.stderr)
            
            # Check if result.md was created
            result_file = workspace / "result.md"
            if result_file.exists():
                print("\n✅ result.md was created!")
                print("\n📖 Result content:")
                print(result_file.read_text())
            else:
                print("\n❌ result.md was not created")
            
            # List all files in workspace
            print("\n📁 Files in workspace:")
            for file in workspace.iterdir():
                print(f"  - {file.name}")
                
        except subprocess.TimeoutExpired:
            print("\n⏱️ Command timed out after 30 seconds")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    test_claude_cli_simple()
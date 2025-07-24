#!/usr/bin/env python3
"""
Debug Claude CLI working directory issue
"""

import subprocess
import tempfile
from pathlib import Path

def test_claude_working_dir():
    """Test Claude CLI with explicit working directory"""
    print("🧪 Testing Claude CLI working directory")
    print("=" * 50)
    
    # Create workspace
    workspace = Path("/tmp/claude-test-debug")
    workspace.mkdir(exist_ok=True)
    
    # Create mission.md
    mission_file = workspace / "mission.md"
    mission_file.write_text("# Mission\n\nPrint 'Hello from Claude!'")
    
    # Create agentInfo.md
    agent_info_file = workspace / "agentInfo.md"
    agent_info_file.write_text("# Agent Info\n\nagentCallbackUrl: http://localhost:8000")
    
    print(f"📁 Created files in: {workspace}")
    print(f"  - mission.md: {mission_file.exists()}")
    print(f"  - agentInfo.md: {agent_info_file.exists()}")
    
    # Test 1: List files
    cmd1 = ["claude", "--print", "--dangerously-skip-permissions", "-p", "List all files in the current directory"]
    print(f"\n🔍 Test 1: List files")
    print(f"Command: {' '.join(cmd1)}")
    result1 = subprocess.run(cmd1, capture_output=True, text=True, cwd=str(workspace))
    print(f"Output: {result1.stdout[:200]}")
    
    # Test 2: Read mission.md
    cmd2 = ["claude", "--print", "--dangerously-skip-permissions", "-p", "Read the mission.md file and tell me what it says"]
    print(f"\n📖 Test 2: Read mission.md")
    print(f"Command: {' '.join(cmd2)}")
    result2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=str(workspace))
    print(f"Output: {result2.stdout[:200]}")
    
    # Test 3: Fixed prompt
    cmd3 = ["claude", "--print", "--dangerously-skip-permissions", "-p", "mission.md 파일을 읽고, 처리한 뒤에 결과를 result.md에 저장하고 agentInfo.md의 agentCallbackUrl을 호출해주세요."]
    print(f"\n🚀 Test 3: Fixed prompt")
    print(f"Command: {' '.join(cmd3[:3])}...")
    result3 = subprocess.run(cmd3, capture_output=True, text=True, cwd=str(workspace), timeout=60)
    print(f"Return code: {result3.returncode}")
    print(f"Output preview: {result3.stdout[:300]}")
    
    # Check result.md
    result_file = workspace / "result.md"
    if result_file.exists():
        print(f"\n✅ result.md created!")
        print(f"Content: {result_file.read_text()[:200]}")
    else:
        print(f"\n❌ result.md not created")
        
    # List final files
    print(f"\n📁 Final files:")
    for f in workspace.iterdir():
        print(f"  - {f.name}")

if __name__ == "__main__":
    test_claude_working_dir()
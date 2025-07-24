#!/usr/bin/env python3
"""
Test Claude CLI with --print option
"""

import subprocess
import tempfile
from pathlib import Path

def test_claude_print():
    """Test Claude CLI with --print option"""
    print("🧪 Testing Claude CLI with --print option")
    print("=" * 50)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        print(f"📁 Workspace: {workspace}")
        
        # Create mission.md
        mission_file = workspace / "mission.md"
        mission_content = """# Mission

간단한 Python 함수를 작성해주세요:
- 함수명: add(a, b)
- 기능: 두 숫자를 더하는 함수
- 예시 포함
"""
        mission_file.write_text(mission_content)
        
        # Create agentInfo.md
        agent_info_file = workspace / "agentInfo.md"
        agent_info_content = """# Agent Information

agentCallbackUrl: http://localhost:8000/api/agent/result
missionId: test_001
agent: claude
"""
        agent_info_file.write_text(agent_info_content)
        
        # Build Claude command with --print
        cmd = [
            "claude", 
            "--print",
            "-p", "mission.md 파일을 읽고, 처리한 뒤에 결과를 result.md에 저장해주세요. agentInfo.md의 정보도 참고하세요."
        ]
        
        print(f"\n🚀 Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(workspace),
                timeout=60
            )
            
            print(f"\n✅ Return code: {result.returncode}")
            
            if result.stdout:
                print("\n📤 Output:")
                print(result.stdout[:1000])  # First 1000 chars
                
            # Check result.md
            result_file = workspace / "result.md"
            if result_file.exists():
                print("\n✅ result.md created!")
                content = result_file.read_text()
                print(f"📖 Content ({len(content)} chars):")
                print(content[:500])
            else:
                print("\n❓ result.md not found")
                
            # List files
            print("\n📁 Files:")
            for f in workspace.iterdir():
                print(f"  - {f.name}")
                
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_claude_print()
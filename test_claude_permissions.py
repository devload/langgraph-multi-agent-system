#!/usr/bin/env python3
"""
Test Claude CLI with permissions bypass for automated execution
"""

import subprocess
import tempfile
from pathlib import Path
import json

def test_claude_with_permissions():
    """Test Claude CLI with permissions bypass"""
    print("🧪 Testing Claude CLI with permissions bypass")
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
        
        # Build Claude command with permissions bypass
        cmd = [
            "claude", 
            "--print",
            "--dangerously-skip-permissions",
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
                print("\n📤 Output preview:")
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
                
            if result.stderr:
                print("\n⚠️ Stderr:")
                print(result.stderr)
                
            # Check result.md
            result_file = workspace / "result.md"
            if result_file.exists():
                print("\n✅ result.md created successfully!")
                content = result_file.read_text()
                print(f"\n📖 result.md content ({len(content)} chars):")
                print("-" * 50)
                print(content[:1000] + "..." if len(content) > 1000 else content)
                print("-" * 50)
            else:
                print("\n❌ result.md not found")
                
            # List all files
            print("\n📁 All files in workspace:")
            for f in workspace.iterdir():
                size = f.stat().st_size if f.is_file() else 0
                print(f"  - {f.name} ({size} bytes)")
                
        except subprocess.TimeoutExpired:
            print("\n⏱️ Command timed out")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_claude_with_permissions()
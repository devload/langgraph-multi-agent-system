#!/usr/bin/env python3
"""
Claude Agent implementation using the base agent class
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_base import AgentBase
from pathlib import Path

class ClaudeAgent(AgentBase):
    def _build_command(self, mission: str) -> list:
        """Build Claude CLI command with fixed prompt format"""
        cmd = [self.config['cli']['command']]
        
        # Add CLI arguments
        cmd.extend(self.config['cli']['args'])
        
        # Fixed prompt format
        cmd.append("-p")
        cmd.append("mission.md 파일을 읽고, 처리한 뒤에 결과를 result.md에 저장하고 agentInfo.md의 agentCallbackUrl을 호출해주세요.")
        
        return cmd
    
    def _prepare_mission_context(self, mission: str, working_dir: Path) -> str:
        """Prepare mission with context for Claude"""
        # Check if there are any existing files to analyze
        existing_files = list(working_dir.glob('*'))
        
        context = mission
        
        if existing_files:
            context += "\n\n## Working Directory Contents:\n"
            for file in existing_files:
                if file.is_file() and file.name not in ['mission.md', 'result.md']:
                    context += f"- {file.name}\n"
        
        # Add specific instructions for Claude
        context += "\n\n## Instructions:\n"
        context += "- Analyze the provided information carefully\n"
        context += "- Provide clear and structured output\n"
        context += "- If you create any files, save them in the current directory\n"
        context += "- Include code examples where appropriate\n"
        
        return context
    
    async def execute_cli(self, mission: str, working_dir: Path) -> dict:
        """Override to create mission.md and agentInfo.md files"""
        # Prepare mission content with context
        enhanced_mission = self._prepare_mission_context(mission, working_dir)
        
        # Create mission.md file
        mission_file = working_dir / "mission.md"
        mission_file.write_text(enhanced_mission)
        
        # Create agentInfo.md file with callback information
        agent_info_file = working_dir / "agentInfo.md"
        agent_info = f"""# Agent Information

## Callback Details
agentCallbackUrl: http://localhost:8000/api/agent/result
missionId: {working_dir.name}
agent: claude

## Instructions
1. Process the mission from mission.md
2. Save your analysis results to result.md
3. After saving result.md, execute this curl command to notify the Hub:

```bash
curl -X POST http://localhost:8000/api/agent/result \\
  -H "Content-Type: application/json" \\
  -d '{{"missionId": "{working_dir.name}", "agent": "claude", "status": "completed", "message": "Analysis completed successfully", "result_path": "{working_dir.absolute()}/result.md"}}'
```

IMPORTANT: You must execute the curl command above to complete the mission.
"""
        agent_info_file.write_text(agent_info)
        
        # Call parent's execute_cli (which will use our fixed prompt)
        return await super().execute_cli(mission, working_dir)

def main():
    """Main entry point"""
    config_path = Path(__file__).parent / "agent_config.yaml"
    
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        sys.exit(1)
    
    agent = ClaudeAgent(str(config_path))
    
    # Get port from environment or use default
    port = int(os.getenv('CLAUDE_AGENT_PORT', '8001'))
    
    agent.run(port=port)

if __name__ == "__main__":
    main()
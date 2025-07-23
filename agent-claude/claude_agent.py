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
        """Build Claude CLI command"""
        cmd = [self.config['cli']['command']]
        
        # Add CLI arguments
        cmd.extend(self.config['cli']['args'])
        
        # Add prompt
        cmd.append(self.config['cli']['prompt_prefix'])
        cmd.append(mission)
        
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
        """Override to add Claude-specific preprocessing"""
        # Prepare mission with context
        enhanced_mission = self._prepare_mission_context(mission, working_dir)
        
        # Call parent's execute_cli with enhanced mission
        return await super().execute_cli(enhanced_mission, working_dir)

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
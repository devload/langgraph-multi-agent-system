#!/usr/bin/env python3
"""
Gemini Agent implementation using the base agent class
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_base import AgentBase
from pathlib import Path
import json

class GeminiAgent(AgentBase):
    def _build_command(self, mission: str) -> list:
        """Build Gemini CLI command"""
        cmd = [self.config['cli']['command']]
        
        # Add CLI arguments
        cmd.extend(self.config['cli']['args'])
        
        # Add prompt
        cmd.append(self.config['cli']['prompt_prefix'])
        cmd.append(mission)
        
        return cmd
    
    def _prepare_mission_context(self, mission: str, working_dir: Path) -> str:
        """Prepare mission with context for Gemini"""
        context = mission
        
        # Check for previous agent results
        previous_results = list(working_dir.parent.glob('*/result.md'))
        
        if previous_results:
            context += "\n\n## Previous Agent Results:\n"
            for result_file in sorted(previous_results):
                agent_name = result_file.parent.name
                if agent_name != working_dir.name:  # Don't include own results
                    context += f"\n### {agent_name} Result:\n"
                    try:
                        content = result_file.read_text()
                        # Extract just the output section
                        if "## Output:" in content:
                            output_section = content.split("## Output:")[1].split("##")[0]
                            context += output_section.strip() + "\n"
                    except:
                        context += "Error reading previous result\n"
        
        # Add Gemini-specific instructions
        context += "\n\n## Instructions for Gemini:\n"
        context += "- Build upon the previous agent's analysis\n"
        context += "- Provide additional insights and recommendations\n"
        context += "- Focus on practical solutions and actionable items\n"
        context += "- Summarize key findings at the end\n"
        
        return context
    
    async def execute_cli(self, mission: str, working_dir: Path) -> dict:
        """Override to add Gemini-specific preprocessing"""
        # Prepare mission with context from previous agents
        enhanced_mission = self._prepare_mission_context(mission, working_dir)
        
        # Call parent's execute_cli with enhanced mission
        result = await super().execute_cli(enhanced_mission, working_dir)
        
        # Post-process result if needed
        if result['status'] == 'success':
            result['message'] = "Gemini analysis completed with enhanced context"
        
        return result

def main():
    """Main entry point"""
    config_path = Path(__file__).parent / "agent_config.yaml"
    
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        sys.exit(1)
    
    agent = GeminiAgent(str(config_path))
    
    # Get port from environment or use default
    port = int(os.getenv('GEMINI_AGENT_PORT', '8002'))
    
    agent.run(port=port)

if __name__ == "__main__":
    main()
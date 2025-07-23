"""
LangGraph Flow Template Generator
Dynamically creates LangGraph workflows from mission configurations
"""

from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
import json

class MissionState(TypedDict):
    """State definition for mission execution"""
    mission: str
    current_agent: str
    results: Dict[str, Any]
    status: str
    history: List[Dict[str, Any]]

def create_agent_node(agent_name: str, agent_config: Dict[str, Any]):
    """Create a node function for an agent"""
    async def agent_node(state: MissionState):
        state["current_agent"] = agent_name
        state["history"].append({
            "agent": agent_name,
            "timestamp": "now",
            "action": "started"
        })
        
        # Agent execution logic would go here
        # In actual implementation, this would call the agent API
        
        return state
    
    return agent_node

def generate_langgraph_flow(workflow_config: Dict[str, Any]) -> str:
    """Generate LangGraph flow code from configuration"""
    
    template = '''"""
Auto-generated LangGraph flow for mission: {mission_id}
Generated at: {timestamp}
"""

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from typing import List, Dict, Any
import asyncio
import httpx

class MissionState(TypedDict):
    mission: str
    current_agent: str
    results: Dict[str, Any]
    status: str
    history: List[Dict[str, Any]]

def create_mission_graph():
    graph = StateGraph(MissionState)
    
    # Agent node definitions
'''
    
    # Add agent nodes
    nodes = set()
    for edge in workflow_config.get("workflow", []):
        if edge["from"] != "start":
            nodes.add(edge["from"])
        if edge["to"] != "end":
            nodes.add(edge["to"])
    
    for node in nodes:
        template += f'''
    async def {node}_node(state: MissionState):
        state["current_agent"] = "{node}"
        state["history"].append({{
            "agent": "{node}",
            "timestamp": "now",
            "action": "started"
        }})
        
        # Send command to {node} agent
        port = {8001 if node == "claude" else 8002}
        async with httpx.AsyncClient() as client:
            await client.post(
                f"http://localhost:{{port}}/api/agent/command",
                json={{
                    "missionId": state.get("mission_id"),
                    "agent": "{node}",
                    "mission": state["mission"]
                }}
            )
        
        return state
    
    graph.add_node("{node}", {node}_node)
'''
    
    # Add edges
    template += '\n    # Edge definitions\n'
    for edge in workflow_config.get("workflow", []):
        if edge["from"] == "start":
            template += f'    graph.set_entry_point("{edge["to"]}")\n'
        elif edge["to"] == "end":
            template += f'    graph.add_edge("{edge["from"]}", END)\n'
        else:
            template += f'    graph.add_edge("{edge["from"]}", "{edge["to"]}")\n'
    
    template += '''
    
    return graph.compile()

# Export the compiled graph
mission_graph = create_mission_graph()
'''
    
    return template

def validate_workflow(workflow: List[Dict[str, str]]) -> bool:
    """Validate workflow configuration"""
    # Check for start node
    has_start = any(edge["from"] == "start" for edge in workflow)
    if not has_start:
        raise ValueError("Workflow must have a 'start' node")
    
    # Check for end node
    has_end = any(edge["to"] == "end" for edge in workflow)
    if not has_end:
        raise ValueError("Workflow must have an 'end' node")
    
    # Check for cycles (simple check)
    # Build adjacency list (one node can have multiple outgoing edges)
    edges = {}
    for edge in workflow:
        if edge["from"] != "start":
            if edge["from"] not in edges:
                edges[edge["from"]] = []
            edges[edge["from"]].append(edge["to"])
    
    def has_cycle(node, path, visited):
        if node in path:
            return True
        if node == "end" or node in visited:
            return False
        
        path.add(node)
        
        if node in edges:
            for next_node in edges[node]:
                if has_cycle(next_node, path.copy(), visited):
                    return True
        
        visited.add(node)
        return False
    
    # Start from first node after 'start'
    start_edges = [edge for edge in workflow if edge["from"] == "start"]
    visited = set()
    for edge in start_edges:
        first_node = edge["to"]
        if has_cycle(first_node, set(), visited):
            raise ValueError("Workflow contains a cycle")
    
    return True

def save_flow_file(mission_id: str, workflow_config: Dict[str, Any], output_dir: str):
    """Generate and save the flow file"""
    import os
    from datetime import datetime
    
    # Validate workflow
    validate_workflow(workflow_config.get("workflow", []))
    
    # Generate flow code
    flow_code = generate_langgraph_flow(workflow_config)
    flow_code = flow_code.format(
        mission_id=mission_id,
        timestamp=datetime.now().isoformat()
    )
    
    # Save to file
    flow_file = os.path.join(output_dir, "flow.py")
    with open(flow_file, "w") as f:
        f.write(flow_code)
    
    return flow_file

if __name__ == "__main__":
    # Example usage
    sample_workflow = {
        "mission_id": "test123",
        "workflow": [
            {"from": "start", "to": "claude"},
            {"from": "claude", "to": "gemini"},
            {"from": "gemini", "to": "end"}
        ]
    }
    
    print(generate_langgraph_flow(sample_workflow))
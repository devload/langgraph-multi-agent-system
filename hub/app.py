#!/usr/bin/env python3
"""
Multi-Agent Mission Hub Server

이 모듈은 LangGraph 기반의 중앙 오케스트레이션 서버입니다.
여러 AI 에이전트(Claude, Gemini)를 관리하고 워크플로우를 실행합니다.

주요 기능:
- 미션 등록 및 관리
- 워크플로우 실행 및 상태 추적
- 에이전트 간 통신 조정
- 결과 수집 및 보고서 생성
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
import json
import os
from datetime import datetime
import asyncio
import httpx
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    # Fallback for testing without langgraph
    print("Warning: LangGraph not installed, using mock implementation")
    class StateGraph:
        def __init__(self, state_type):
            self.nodes = {}
            self.edges = {}
            self.entry = None
        def add_node(self, name, func):
            self.nodes[name] = func
        def add_edge(self, from_node, to_node):
            self.edges[from_node] = to_node
        def set_entry_point(self, node):
            self.entry = node
        def compile(self, checkpointer=None):
            return MockGraph(self)
    
    class MockGraph:
        def __init__(self, graph):
            self.graph = graph
        async def ainvoke(self, state, config):
            # Simple mock execution
            return state
    
    END = "END"
    class SqliteSaver:
        @staticmethod
        def from_conn_string(conn):
            return None
from typing_extensions import TypedDict
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mission_history import MissionHistory

app = FastAPI(title="Multi-Agent Mission Hub")

# Initialize mission history
history = MissionHistory()

# Pydantic 모델 정의
class WorkflowEdge(BaseModel):
    """워크플로우 엣지 모델 - 노드 간 연결을 정의"""
    from_node: str = Field(alias="from")  # 시작 노드
    to_node: str = Field(alias="to")      # 도착 노드

class MissionRegisterRequest(BaseModel):
    workflow: List[WorkflowEdge]
    mission: str

class MissionRunRequest(BaseModel):
    pass

class AgentCommandRequest(BaseModel):
    missionId: str
    agent: str
    mission: str

class AgentResultRequest(BaseModel):
    missionId: str
    agent: str
    status: str
    message: str
    result_path: str

class MissionState(TypedDict):
    """미션 실행 상태를 추적하는 타입 정의"""
    mission: str           # 미션 설명
    current_agent: str     # 현재 실행 중인 에이전트
    results: Dict[str, str]  # 각 에이전트의 실행 결과
    status: str            # 전체 미션 상태

# Global mission storage
missions: Dict[str, Dict] = {}

# LangGraph checkpointer
checkpointer = SqliteSaver.from_conn_string(":memory:")

def create_mission_graph(workflow: List[WorkflowEdge], mission_id: str):
    """
    미션을 위한 LangGraph 인스턴스 생성
    
    Args:
        workflow: 워크플로우 엣지 리스트
        mission_id: 미션 고유 ID
        
    Returns:
        컴파일된 LangGraph 인스턴스
    """
    graph = StateGraph(MissionState)
    
    # Extract unique nodes
    nodes = set()
    for edge in workflow:
        if edge.from_node != "start":
            nodes.add(edge.from_node)
        if edge.to_node != "end":
            nodes.add(edge.to_node)
    
    # Add nodes
    for node in nodes:
        async def agent_node(state: MissionState, agent_name=node):
            state["current_agent"] = agent_name
            state["status"] = "running"
            
            # Send command to agent
            agent_port = 8001 if agent_name == "claude" else 8002
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"http://localhost:{agent_port}/api/agent/command",
                    json={
                        "missionId": mission_id,
                        "agent": agent_name,
                        "mission": state["mission"]
                    }
                )
            
            # Wait for result (in real implementation, use proper async handling)
            await asyncio.sleep(1)
            return state
        
        graph.add_node(node, agent_node)
    
    # Add edges
    for edge in workflow:
        if edge.from_node == "start":
            graph.set_entry_point(edge.to_node)
        elif edge.to_node == "end":
            graph.add_edge(edge.from_node, END)
        else:
            graph.add_edge(edge.from_node, edge.to_node)
    
    return graph.compile(checkpointer=checkpointer)

def generate_mermaid(workflow: List[WorkflowEdge]) -> str:
    """Generate Mermaid diagram from workflow"""
    mermaid = "graph TD\n"
    for edge in workflow:
        from_node = edge.from_node
        to_node = edge.to_node
        mermaid += f"    {from_node} --> {to_node}\n"
    return mermaid

@app.post("/api/mission/register")
async def register_mission(request: MissionRegisterRequest):
    """
    새로운 미션 등록
    
    워크플로우와 미션 설명을 받아 새로운 미션을 생성합니다.
    각 미션은 고유 ID를 부여받고 별도의 디렉토리에 저장됩니다.
    
    Args:
        request: 워크플로우와 미션 정보를 포함한 요청
        
    Returns:
        미션 ID와 상태를 포함한 응답
        
    Raises:
        HTTPException: 워크플로우 검증 실패 시
    """
    from flow_template import validate_workflow
    
    # Validate workflow first
    try:
        validate_workflow([edge.dict() for edge in request.workflow])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    mission_id = str(uuid.uuid4())[:8]
    
    # Create mission directory
    mission_dir = f"hub/missions/{mission_id}"
    os.makedirs(mission_dir, exist_ok=True)
    
    # Save configuration
    config = {
        "missionId": mission_id,
        "workflow": [edge.dict() for edge in request.workflow],
        "mission": request.mission,
        "status": "registered",
        "created_at": datetime.now().isoformat()
    }
    
    with open(f"{mission_dir}/config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Generate and save Mermaid diagram
    mermaid = generate_mermaid(request.workflow)
    with open(f"{mission_dir}/graph.mmd", "w") as f:
        f.write(mermaid)
    
    # Create LangGraph instance
    graph = create_mission_graph(request.workflow, mission_id)
    
    # Store in memory
    missions[mission_id] = {
        "config": config,
        "graph": graph,
        "state": {
            "mission": request.mission,
            "current_agent": "start",
            "results": {},
            "status": "registered"
        }
    }
    
    # Record in history
    history.record_mission_created(
        mission_id,
        [edge.dict() for edge in request.workflow],
        request.mission
    )
    
    return {
        "missionId": mission_id,
        "status": "registered"
    }

@app.get("/api/mission/{mission_id}/graph")
async def get_mission_graph(mission_id: str):
    """Get mission workflow visualization"""
    if mission_id not in missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    mission_dir = f"hub/missions/{mission_id}"
    if not os.path.exists(f"{mission_dir}/graph.mmd"):
        raise HTTPException(status_code=404, detail="Graph not found")
    
    with open(f"{mission_dir}/graph.mmd", "r") as f:
        mermaid = f.read()
    
    return {"mermaid": mermaid}

@app.post("/api/mission/{mission_id}/run")
async def run_mission(mission_id: str):
    """Execute a registered mission"""
    if mission_id not in missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    mission = missions[mission_id]
    graph = mission["graph"]
    
    # Update status
    mission["state"]["status"] = "running"
    missions[mission_id]["config"]["status"] = "running"
    
    # Record in history
    history.record_mission_started(mission_id)
    
    # Run graph asynchronously
    asyncio.create_task(execute_mission(mission_id, graph, mission["state"]))
    
    return {
        "missionId": mission_id,
        "status": "running"
    }

async def execute_mission(mission_id: str, graph, initial_state):
    """Execute mission graph"""
    try:
        config = {"configurable": {"thread_id": mission_id}}
        await graph.ainvoke(initial_state, config)
        missions[mission_id]["state"]["status"] = "completed"
        history.record_mission_completed(mission_id, "completed")
    except Exception as e:
        missions[mission_id]["state"]["status"] = "failed"
        missions[mission_id]["state"]["error"] = str(e)
        history.record_mission_completed(mission_id, "failed")
        history.add_log(mission_id, "ERROR", "Hub", str(e))

@app.post("/api/agent/result")
async def receive_agent_result(request: AgentResultRequest):
    """Receive results from agents"""
    if request.missionId not in missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Update mission state
    missions[request.missionId]["state"]["results"][request.agent] = {
        "status": request.status,
        "message": request.message,
        "result_path": request.result_path,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save result reference
    mission_dir = f"hub/missions/{request.missionId}"
    results_file = f"{mission_dir}/results.json"
    
    results = {}
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            results = json.load(f)
    
    results[request.agent] = {
        "status": request.status,
        "message": request.message,
        "result_path": request.result_path,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Record in history
    history.record_agent_execution(
        request.missionId,
        request.agent,
        request.status,
        datetime.fromisoformat(missions[request.missionId]["state"]["results"][request.agent].get("timestamp", datetime.now().isoformat())),
        datetime.now(),
        request.result_path,
        request.message if request.status == "error" else None
    )
    
    return {"status": "received"}

@app.get("/api/mission/{mission_id}/status")
async def get_mission_status(mission_id: str):
    """Get mission execution status"""
    if mission_id not in missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return {
        "missionId": mission_id,
        "status": missions[mission_id]["state"]["status"],
        "current_agent": missions[mission_id]["state"]["current_agent"],
        "results": missions[mission_id]["state"]["results"]
    }

@app.get("/api/mission/{mission_id}/results/{agent}")
async def get_agent_result(mission_id: str, agent: str):
    """Get specific agent's result content"""
    if mission_id not in missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    results = missions[mission_id]["state"]["results"]
    if agent not in results:
        raise HTTPException(status_code=404, detail=f"No results from agent {agent}")
    
    agent_result = results[agent]
    result_path = agent_result.get("result_path")
    
    if not result_path or not os.path.exists(result_path):
        return {
            "agent": agent,
            "status": agent_result.get("status"),
            "message": agent_result.get("message"),
            "content": "Result file not found"
        }
    
    try:
        with open(result_path, 'r') as f:
            content = f.read()
        
        return {
            "agent": agent,
            "status": agent_result.get("status"),
            "message": agent_result.get("message"),
            "timestamp": agent_result.get("timestamp"),
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading result file: {str(e)}")

@app.get("/api/mission/{mission_id}/results")
async def get_all_results(mission_id: str):
    """Get all agents' results for a mission"""
    if mission_id not in missions:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    all_results = {}
    results = missions[mission_id]["state"]["results"]
    
    for agent, agent_result in results.items():
        result_path = agent_result.get("result_path")
        content = "No content available"
        
        if result_path and os.path.exists(result_path):
            try:
                with open(result_path, 'r') as f:
                    content = f.read()
            except:
                content = "Error reading result file"
        
        all_results[agent] = {
            "status": agent_result.get("status"),
            "message": agent_result.get("message"),
            "timestamp": agent_result.get("timestamp"),
            "content": content
        }
    
    return {
        "missionId": mission_id,
        "status": missions[mission_id]["state"]["status"],
        "results": all_results
    }

@app.get("/api/missions")
async def list_missions(status: Optional[str] = None, limit: int = 10):
    """List all missions with optional status filter"""
    mission_list = []
    
    for mission_id, mission_data in missions.items():
        mission_status = mission_data["state"]["status"]
        
        if status and mission_status != status:
            continue
        
        mission_list.append({
            "missionId": mission_id,
            "status": mission_status,
            "mission": mission_data["config"]["mission"][:100] + "...",
            "created_at": mission_data["config"].get("created_at"),
            "current_agent": mission_data["state"].get("current_agent"),
            "agent_count": len(mission_data["state"].get("results", {}))
        })
    
    # Sort by creation time
    mission_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "total": len(mission_list),
        "missions": mission_list[:limit]
    }

@app.get("/api/mission/{mission_id}/history")
async def get_mission_history(mission_id: str):
    """Get complete mission history with logs"""
    history_data = history.get_mission_history(mission_id)
    
    if not history_data:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return history_data

@app.get("/api/stats")
async def get_mission_stats(limit: int = 100):
    """Get mission execution statistics"""
    return history.get_mission_stats(limit)

@app.get("/api/mission/{mission_id}/report")
async def export_mission_report(mission_id: str):
    """Export mission report as markdown"""
    try:
        report_path = f"hub/missions/{mission_id}/report.md"
        history.export_mission_report(mission_id, report_path)
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        return {
            "missionId": mission_id,
            "report_path": report_path,
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
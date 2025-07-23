from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI(title="Mock Claude Agent")

class AgentCommandRequest(BaseModel):
    missionId: str
    agent: str
    mission: str

@app.post("/api/agent/command")
async def receive_command(request: AgentCommandRequest):
    print(f"Mock Claude received: {request.mission}")
    
    # Simulate processing
    await asyncio.sleep(2)
    
    # Send result back
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8000/api/agent/result",
            json={
                "missionId": request.missionId,
                "agent": "claude",
                "status": "success",
                "message": "Mock Claude completed processing",
                "result_path": "/tmp/claude_result.md"
            }
        )
    
    return {"status": "success"}

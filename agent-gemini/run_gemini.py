from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import httpx
import asyncio
from datetime import datetime

app = FastAPI(title="Gemini Agent")

class AgentCommandRequest(BaseModel):
    missionId: str
    agent: str
    mission: str

@app.post("/api/agent/command")
async def receive_command(request: AgentCommandRequest):
    """Receive command from Hub and execute Gemini CLI"""
    
    # Save mission to file
    mission_file = "mission.md"
    with open(mission_file, "w") as f:
        f.write(f"# Mission ID: {request.missionId}\n\n")
        f.write(f"## Agent: {request.agent}\n\n")
        f.write(f"## Mission:\n{request.mission}\n")
    
    # Execute Gemini CLI
    try:
        cmd = [
            "gemini",
            "--yolo",
            "-p",
            f"{request.mission}"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Save result
        result_file = "result.md"
        with open(result_file, "w") as f:
            f.write(f"# Gemini Result\n\n")
            f.write(f"## Mission ID: {request.missionId}\n\n")
            f.write(f"## Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(f"## Status: {'success' if result.returncode == 0 else 'failed'}\n\n")
            f.write(f"## Output:\n```\n{result.stdout}\n```\n\n")
            if result.stderr:
                f.write(f"## Errors:\n```\n{result.stderr}\n```\n")
        
        # Send result back to Hub
        await send_result_to_hub(
            request.missionId,
            request.agent,
            "success" if result.returncode == 0 else "failed",
            "Gemini processing completed",
            os.path.abspath(result_file)
        )
        
        return {"status": "success", "message": "Command executed"}
        
    except subprocess.TimeoutExpired:
        await send_result_to_hub(
            request.missionId,
            request.agent,
            "timeout",
            "Gemini CLI execution timed out",
            ""
        )
        return {"status": "error", "message": "Execution timed out"}
        
    except Exception as e:
        await send_result_to_hub(
            request.missionId,
            request.agent,
            "error",
            str(e),
            ""
        )
        return {"status": "error", "message": str(e)}

async def send_result_to_hub(mission_id: str, agent: str, status: str, message: str, result_path: str):
    """Send execution result back to Hub"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://localhost:8000/api/agent/result",
                json={
                    "missionId": mission_id,
                    "agent": agent,
                    "status": status,
                    "message": message,
                    "result_path": result_path
                }
            )
        except Exception as e:
            print(f"Failed to send result to hub: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
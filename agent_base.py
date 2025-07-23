#!/usr/bin/env python3
"""
에이전트 베이스 클래스

Claude와 Gemini 같은 CLI 기반 AI 에이전트를 통합하기 위한 추상 클래스입니다.
주요 기능:
- CLI 명령 실행 및 결과 수집
- Hub와의 통신
- 미션 작업 공간 관리
- 비동기 실행 및 타임아웃 처리
"""

from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import yaml
import logging
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
import shutil
from typing import Optional, Dict, Any

class AgentCommandRequest(BaseModel):
    missionId: str
    agent: str
    mission: str

class AgentBase(ABC):
    def __init__(self, config_path: str):
        """
        에이전트 초기화
        
        Args:
            config_path: YAML 설정 파일 경로
        """
        self.config = self._load_config(config_path)
        self.agent_name = self.config['agent']['name']
        self.workspace_dir = Path(self.config['files']['workspace_dir'])
        self.setup_logging()
        self.app = FastAPI(title=f"{self.agent_name.title()} Agent")
        self._setup_routes()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['logging']['level'])
        log_file = self.config['logging']['file']
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.agent_name)
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        @self.app.post("/api/agent/command")
        async def receive_command(request: AgentCommandRequest):
            return await self.handle_command(request)
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "agent": self.agent_name}
    
    async def handle_command(self, request: AgentCommandRequest):
        """
        Hub로부터 받은 명령 처리
        
        1. 미션 작업 공간 생성
        2. 미션 파일 저장
        3. CLI 명령 실행
        4. 결과 파일 저장
        5. Hub로 결과 전송
        
        Args:
            request: 미션 ID, 에이전트 이름, 미션 내용을 포함한 요청
            
        Returns:
            실행 상태와 메시지를 포함한 응답
        """
        self.logger.info(f"Received mission {request.missionId}: {request.mission[:50]}...")
        
        # Create mission workspace
        mission_dir = self.workspace_dir / request.missionId
        mission_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save mission details
            mission_file = mission_dir / self.config['files']['mission_file']
            self._save_mission_file(mission_file, request)
            
            # Execute CLI command
            result = await self.execute_cli(request.mission, mission_dir)
            
            # Save result
            result_file = mission_dir / self.config['files']['result_file']
            self._save_result_file(result_file, request.missionId, result)
            
            # Send result back to Hub
            await self._send_result_to_hub(
                request.missionId,
                request.agent,
                result['status'],
                result['message'],
                str(result_file.absolute())
            )
            
            return {"status": "success", "message": "Command executed"}
            
        except Exception as e:
            self.logger.error(f"Error processing mission {request.missionId}: {str(e)}")
            await self._send_result_to_hub(
                request.missionId,
                request.agent,
                "error",
                str(e),
                ""
            )
            return {"status": "error", "message": str(e)}
    
    def _save_mission_file(self, file_path: Path, request: AgentCommandRequest):
        """Save mission details to file"""
        content = f"""# Mission ID: {request.missionId}

## Agent: {request.agent}

## Timestamp: {datetime.now().isoformat()}

## Mission:
{request.mission}

---
"""
        file_path.write_text(content)
        self.logger.info(f"Saved mission to {file_path}")
    
    def _save_result_file(self, file_path: Path, mission_id: str, result: Dict[str, Any]):
        """Save execution result to file"""
        content = f"""# {self.agent_name.title()} Result

## Mission ID: {mission_id}

## Timestamp: {datetime.now().isoformat()}

## Status: {result['status']}

## Execution Time: {result.get('execution_time', 'N/A')} seconds

## Output:
```
{result.get('stdout', '')}
```

"""
        if result.get('stderr'):
            content += f"""## Errors:
```
{result['stderr']}
```
"""
        
        if result.get('files_created'):
            content += f"\n## Files Created:\n"
            for file in result['files_created']:
                content += f"- {file}\n"
        
        file_path.write_text(content)
        self.logger.info(f"Saved result to {file_path}")
    
    async def execute_cli(self, mission: str, working_dir: Path) -> Dict[str, Any]:
        """
        CLI 명령 실행 (비동기)
        
        서브클래스에서 _build_command를 구현하여 사용합니다.
        타임아웃, 파일 생성 추적, 에러 처리를 포함합니다.
        
        Args:
            mission: 실행할 미션 내용
            working_dir: 작업 디렉토리
            
        Returns:
            실행 결과를 포함한 딕셔너리
            - status: 성공/실패/타임아웃
            - stdout/stderr: 출력 내용
            - execution_time: 실행 시간
            - files_created: 생성된 파일 목록
        """
        start_time = datetime.now()
        
        # Build command
        cmd = self._build_command(mission)
        self.logger.info(f"Executing command: {' '.join(cmd[:3])}...")
        
        # Execute
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(working_dir)
            )
            
            # Wait with timeout
            timeout = self.config['agent']['timeout']
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Check for created files
            files_created = self._find_created_files(working_dir, start_time)
            
            return {
                'status': 'success' if process.returncode == 0 else 'failed',
                'stdout': stdout.decode('utf-8', errors='replace'),
                'stderr': stderr.decode('utf-8', errors='replace'),
                'return_code': process.returncode,
                'execution_time': execution_time,
                'files_created': files_created,
                'message': f"{self.agent_name} processing completed"
            }
            
        except asyncio.TimeoutError:
            self.logger.error(f"Command timed out after {timeout} seconds")
            return {
                'status': 'timeout',
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'return_code': -1,
                'execution_time': timeout,
                'message': f"{self.agent_name} CLI execution timed out"
            }
        except Exception as e:
            self.logger.error(f"Command execution failed: {str(e)}")
            return {
                'status': 'error',
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'message': f"Error executing {self.agent_name} CLI"
            }
    
    @abstractmethod
    def _build_command(self, mission: str) -> list:
        """
        CLI 명령 구성 (추상 메서드)
        
        서브클래스에서 반드시 구현해야 합니다.
        각 에이전트의 CLI 호출 방식에 맞게 명령을 구성합니다.
        
        Args:
            mission: 실행할 미션 내용
            
        Returns:
            CLI 명령 리스트 [실행파일, 옵션, ...]
        """
        pass
    
    def _find_created_files(self, working_dir: Path, start_time: datetime) -> list:
        """Find files created after start_time in working directory"""
        created_files = []
        
        for file_path in working_dir.rglob('*'):
            if file_path.is_file():
                # Check if file was created after start_time
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime > start_time:
                    # Store relative path
                    relative_path = file_path.relative_to(working_dir)
                    created_files.append(str(relative_path))
        
        return created_files
    
    async def _send_result_to_hub(self, mission_id: str, agent: str, 
                                 status: str, message: str, result_path: str):
        """Send execution result back to Hub"""
        hub_url = os.getenv('HUB_URL', 'http://localhost:8000')
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{hub_url}/api/agent/result",
                    json={
                        "missionId": mission_id,
                        "agent": agent,
                        "status": status,
                        "message": message,
                        "result_path": result_path
                    },
                    timeout=30.0
                )
                self.logger.info(f"Result sent to hub: {response.status_code}")
            except Exception as e:
                self.logger.error(f"Failed to send result to hub: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8001):
        """Run the agent server"""
        import uvicorn
        self.logger.info(f"Starting {self.agent_name} agent on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)
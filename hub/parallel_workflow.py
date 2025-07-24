#!/usr/bin/env python3
"""
병렬 워크플로우 지원 모듈

여러 에이전트를 동시에 실행하고 결과를 통합하는 기능을 제공합니다.
"""

from typing import List, Dict, Any, TypedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import httpx
from datetime import datetime
import json

class ParallelWorkflowState(TypedDict):
    """병렬 워크플로우 상태"""
    mission: str
    parallel_agents: List[str]
    agent_prompts: Dict[str, str]  # 에이전트별 특화된 프롬프트
    results: Dict[str, Any]
    status: str
    start_time: datetime
    end_time: datetime

async def execute_agent_async(agent_name: str, mission: str, agent_url: str) -> Dict[str, Any]:
    """비동기로 에이전트 실행"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{agent_url}/execute",
                json={"mission": mission},
                timeout=300.0
            )
            if response.status_code == 200:
                return {
                    "agent": agent_name,
                    "status": "success",
                    "result": response.json()
                }
            else:
                return {
                    "agent": agent_name,
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "agent": agent_name,
                "status": "error",
                "error": str(e)
            }

def create_specialized_prompts(base_mission: str) -> Dict[str, str]:
    """각 에이전트를 위한 특화된 프롬프트 생성"""
    
    prompts = {
        "security": f"""
As a security specialist, analyze the code for:
- SQL Injection vulnerabilities
- XSS (Cross-Site Scripting) risks  
- Authentication and authorization issues
- Hardcoded credentials or secrets
- Insecure cryptographic practices
- Input validation problems

Base requirement: {base_mission}

Focus specifically on security vulnerabilities and provide:
1. Severity level (Critical/High/Medium/Low)
2. CWE classification
3. Specific remediation steps
4. Security best practices
""",
        
        "performance": f"""
As a performance optimization expert, analyze the code for:
- Algorithm complexity (Big O notation)
- Memory leaks and inefficient memory usage
- Database query optimization opportunities
- Caching opportunities
- Unnecessary loops or redundant operations
- Resource management issues

Base requirement: {base_mission}

Provide specific metrics and expected performance improvements.
""",
        
        "architecture": f"""
As a software architect, evaluate the code for:
- SOLID principles compliance
- Design pattern usage and opportunities
- Module coupling and cohesion
- Separation of concerns
- Scalability considerations
- Error handling patterns

Base requirement: {base_mission}

Suggest architectural improvements and refactoring strategies.
""",
        
        "testing": f"""
As a QA engineer, assess the code for:
- Test coverage gaps
- Testability issues
- Missing edge cases
- Mock/stub opportunities
- Integration test requirements
- Performance test needs

Base requirement: {base_mission}

Recommend specific test cases and testing strategies.
""",
        
        "documentation": f"""
As a technical writer, review the code for:
- Missing or inadequate docstrings
- Unclear variable/function names
- Complex logic without comments
- API documentation needs
- Example usage documentation
- Configuration documentation

Base requirement: {base_mission}

Suggest documentation improvements and best practices.
"""
    }
    
    return prompts

def create_parallel_workflow_graph():
    """병렬 실행을 위한 워크플로우 그래프 생성"""
    from langgraph.graph import StateGraph, END
    
    workflow = StateGraph(ParallelWorkflowState)
    
    def distribute_tasks(state: ParallelWorkflowState) -> ParallelWorkflowState:
        """작업을 여러 에이전트에 분배"""
        state['agent_prompts'] = create_specialized_prompts(state['mission'])
        state['status'] = 'distributed'
        return state
    
    async def execute_parallel(state: ParallelWorkflowState) -> ParallelWorkflowState:
        """모든 에이전트를 병렬로 실행"""
        state['status'] = 'executing'
        state['start_time'] = datetime.now()
        
        # 에이전트 URL 매핑
        agent_urls = {
            "security": "http://localhost:8001",
            "performance": "http://localhost:8002", 
            "architecture": "http://localhost:8003",
            "testing": "http://localhost:8004",
            "documentation": "http://localhost:8005"
        }
        
        # 병렬 실행
        tasks = []
        for agent in state['parallel_agents']:
            if agent in state['agent_prompts']:
                prompt = state['agent_prompts'][agent]
                url = agent_urls.get(agent, f"http://localhost:800{len(tasks)+1}")
                tasks.append(execute_agent_async(agent, prompt, url))
        
        # 모든 작업 완료 대기
        results = await asyncio.gather(*tasks)
        
        # 결과 저장
        for result in results:
            agent_name = result['agent']
            state['results'][agent_name] = result
        
        state['end_time'] = datetime.now()
        state['status'] = 'completed'
        
        return state
    
    def synthesize_results(state: ParallelWorkflowState) -> ParallelWorkflowState:
        """모든 결과를 종합"""
        # 여기서 결과를 통합하여 최종 보고서 생성
        state['status'] = 'synthesized'
        return state
    
    # 워크플로우 구성
    workflow.add_node("distribute", distribute_tasks)
    workflow.add_node("execute_parallel", execute_parallel)
    workflow.add_node("synthesize", synthesize_results)
    
    workflow.set_entry_point("distribute")
    workflow.add_edge("distribute", "execute_parallel")
    workflow.add_edge("execute_parallel", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()

def register_parallel_agents():
    """병렬 에이전트들을 시스템에 등록"""
    agents = [
        {
            "name": "security",
            "description": "Security vulnerability analysis",
            "port": 8001,
            "specialization": "OWASP Top 10, CWE, secure coding"
        },
        {
            "name": "performance", 
            "description": "Performance optimization analysis",
            "port": 8002,
            "specialization": "Algorithm complexity, caching, database optimization"
        },
        {
            "name": "architecture",
            "description": "Software architecture analysis", 
            "port": 8003,
            "specialization": "SOLID, design patterns, clean architecture"
        },
        {
            "name": "testing",
            "description": "Test coverage and quality analysis",
            "port": 8004,
            "specialization": "Unit testing, integration testing, TDD"
        },
        {
            "name": "documentation",
            "description": "Documentation quality analysis",
            "port": 8005,
            "specialization": "API docs, code comments, README files"
        }
    ]
    
    return agents

# 병렬 워크플로우 예제
PARALLEL_WORKFLOW_EXAMPLES = {
    "comprehensive_analysis": {
        "name": "Comprehensive Code Analysis",
        "agents": ["security", "performance", "architecture", "testing", "documentation"],
        "description": "Full analysis covering all aspects of code quality"
    },
    "security_performance": {
        "name": "Security & Performance Focus",
        "agents": ["security", "performance"],
        "description": "Focused analysis on security vulnerabilities and performance issues"
    },
    "quality_assurance": {
        "name": "QA Complete", 
        "agents": ["testing", "documentation", "architecture"],
        "description": "Quality assurance focused on testing, docs, and structure"
    }
}
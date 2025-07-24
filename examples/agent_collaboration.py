#!/usr/bin/env python3
"""
에이전트 협업 패턴 예제

여러 에이전트가 서로의 분석 결과를 참고하여 더 깊이있는 분석을 수행합니다.
- Sequential Collaboration: 순차적 협업
- Conditional Routing: 조건부 라우팅
- Feedback Loop: 피드백 루프
"""

from typing import TypedDict, List, Dict, Any, Optional
import json
from datetime import datetime
from enum import Enum

# Mock LangGraph imports
from multi_agent_system import StateGraph, CompiledGraph, END

class CollaborationPattern(Enum):
    """협업 패턴 타입"""
    SEQUENTIAL = "sequential"  # A → B → C
    PARALLEL_MERGE = "parallel_merge"  # (A || B || C) → Merge
    CONDITIONAL = "conditional"  # A → (B if X else C)
    FEEDBACK_LOOP = "feedback_loop"  # A → B → A → Final
    HIERARCHICAL = "hierarchical"  # Master → (Worker1, Worker2) → Master

class CollaborationState(TypedDict):
    """협업 워크플로우 상태"""
    code_path: str
    mission: str
    pattern: str
    agent_results: Dict[str, Any]
    collaboration_context: Dict[str, Any]  # 에이전트 간 공유 컨텍스트
    decision_points: List[Dict[str, Any]]
    final_report: str
    status: str

# 전문 에이전트들
def security_analyzer(state: CollaborationState) -> CollaborationState:
    """보안 분석 에이전트"""
    print("🔐 Security Analyzer: 초기 보안 분석 중...")
    
    security_findings = {
        "vulnerabilities": [
            {"type": "SQL Injection", "severity": "critical", "confidence": 0.95},
            {"type": "XSS", "severity": "high", "confidence": 0.80},
            {"type": "Weak Auth", "severity": "medium", "confidence": 0.70}
        ],
        "risk_score": 8.5,
        "requires_immediate_action": True
    }
    
    state['agent_results']['security'] = security_findings
    state['collaboration_context']['high_risk'] = security_findings['risk_score'] > 7
    state['collaboration_context']['critical_vulnerabilities'] = [
        v for v in security_findings['vulnerabilities'] 
        if v['severity'] == 'critical'
    ]
    
    return state

def performance_analyzer(state: CollaborationState) -> CollaborationState:
    """성능 분석 에이전트"""
    print("⚡ Performance Analyzer: 성능 분석 중...")
    
    # 보안 분석 결과 참조
    security_context = state['agent_results'].get('security', {})
    
    performance_findings = {
        "bottlenecks": [
            {"type": "N+1 Query", "impact": "high", "location": "UserService"},
            {"type": "Memory Leak", "impact": "critical", "location": "CacheManager"}
        ],
        "optimization_score": 5.5
    }
    
    # 보안 이슈가 성능에 미치는 영향 분석
    if security_context.get('requires_immediate_action'):
        performance_findings['security_impact'] = {
            "description": "보안 패치가 성능에 영향을 줄 수 있음",
            "estimated_overhead": "10-15%"
        }
    
    state['agent_results']['performance'] = performance_findings
    state['collaboration_context']['needs_architecture_review'] = (
        performance_findings['optimization_score'] < 6
    )
    
    return state

def architecture_reviewer(state: CollaborationState) -> CollaborationState:
    """아키텍처 검토 에이전트"""
    print("🏗️ Architecture Reviewer: 구조 검토 중...")
    
    # 이전 에이전트들의 분석 참조
    security = state['agent_results'].get('security', {})
    performance = state['agent_results'].get('performance', {})
    
    review = {
        "design_issues": [],
        "recommendations": []
    }
    
    # 보안과 성능 이슈를 고려한 아키텍처 개선안
    if state['collaboration_context'].get('high_risk'):
        review['design_issues'].append({
            "issue": "Security layer가 비즈니스 로직과 혼재",
            "solution": "보안 관심사 분리 (Security Aspect 도입)"
        })
        review['recommendations'].append(
            "인증/인가를 위한 별도의 미들웨어 계층 추가"
        )
    
    if state['collaboration_context'].get('needs_architecture_review'):
        review['design_issues'].append({
            "issue": "데이터 접근 계층의 비효율적 설계",
            "solution": "Repository 패턴과 캐싱 전략 도입"
        })
    
    state['agent_results']['architecture'] = review
    return state

def test_strategist(state: CollaborationState) -> CollaborationState:
    """테스트 전략 수립 에이전트"""
    print("🧪 Test Strategist: 테스트 전략 수립 중...")
    
    # 모든 이전 분석 결과를 종합
    all_issues = []
    
    if 'security' in state['agent_results']:
        all_issues.extend([
            f"Security: {v['type']}" 
            for v in state['agent_results']['security']['vulnerabilities']
        ])
    
    if 'performance' in state['agent_results']:
        all_issues.extend([
            f"Performance: {b['type']}" 
            for b in state['agent_results']['performance']['bottlenecks']
        ])
    
    test_strategy = {
        "priority_tests": [],
        "test_coverage_target": 85,
        "special_focus_areas": []
    }
    
    # 발견된 이슈에 대한 테스트 케이스 생성
    for issue in all_issues:
        if "SQL Injection" in issue:
            test_strategy["priority_tests"].append({
                "test": "SQL Injection prevention test",
                "type": "security",
                "priority": "critical"
            })
        elif "N+1 Query" in issue:
            test_strategy["priority_tests"].append({
                "test": "Database query optimization test",
                "type": "performance",
                "priority": "high"
            })
    
    state['agent_results']['testing'] = test_strategy
    return state

def synthesizer(state: CollaborationState) -> CollaborationState:
    """결과 종합 에이전트"""
    print("📊 Synthesizer: 분석 결과 종합 중...")
    
    report = f"""# 🤝 Multi-Agent Collaboration Analysis Report

**File**: {state['code_path']}  
**Collaboration Pattern**: {state['pattern']}  
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🔄 협업 프로세스

"""
    
    # 협업 흐름 시각화
    if state['pattern'] == CollaborationPattern.SEQUENTIAL.value:
        report += "Security → Performance → Architecture → Testing\n\n"
    elif state['pattern'] == CollaborationPattern.FEEDBACK_LOOP.value:
        report += "Security ↔ Performance → Architecture → Testing\n\n"
    
    # 각 에이전트의 주요 발견사항
    report += "## 📋 에이전트별 분석 결과\n\n"
    
    for agent, results in state['agent_results'].items():
        report += f"### {agent.capitalize()} Agent\n"
        
        if agent == 'security':
            report += f"- **위험도 점수**: {results.get('risk_score', 'N/A')}/10\n"
            report += f"- **발견된 취약점**: {len(results.get('vulnerabilities', []))}개\n"
            
        elif agent == 'performance':
            report += f"- **최적화 점수**: {results.get('optimization_score', 'N/A')}/10\n"
            report += f"- **병목 지점**: {len(results.get('bottlenecks', []))}개\n"
            
        elif agent == 'architecture':
            report += f"- **설계 이슈**: {len(results.get('design_issues', []))}개\n"
            report += f"- **권장사항**: {len(results.get('recommendations', []))}개\n"
            
        elif agent == 'testing':
            report += f"- **우선순위 테스트**: {len(results.get('priority_tests', []))}개\n"
            report += f"- **목표 커버리지**: {results.get('test_coverage_target', 'N/A')}%\n"
        
        report += "\n"
    
    # 협업을 통한 인사이트
    report += "## 💡 협업을 통한 주요 인사이트\n\n"
    
    if state['collaboration_context'].get('high_risk'):
        report += "### 🚨 고위험 상태\n"
        report += "- 보안 팀이 발견한 심각한 취약점으로 인해 즉각적인 조치 필요\n"
        report += "- 성능 팀은 보안 패치가 10-15% 성능 저하를 야기할 수 있다고 분석\n"
        report += "- 아키텍처 팀은 보안 계층 분리를 통한 근본적 해결 제안\n\n"
    
    if state['collaboration_context'].get('needs_architecture_review'):
        report += "### 🏗️ 구조 개선 필요\n"
        report += "- 성능 문제의 근본 원인이 아키텍처 설계에 있음\n"
        report += "- Repository 패턴 도입으로 성능과 유지보수성 동시 개선 가능\n\n"
    
    # 통합 액션 플랜
    report += "## 📌 통합 액션 플랜\n\n"
    report += "### Phase 1: 긴급 조치 (1-2일)\n"
    report += "1. Critical 보안 취약점 패치\n"
    report += "2. 메모리 누수 해결\n\n"
    
    report += "### Phase 2: 구조 개선 (1주일)\n"
    report += "1. 보안 미들웨어 계층 구현\n"
    report += "2. 데이터 접근 계층 리팩토링\n\n"
    
    report += "### Phase 3: 품질 보증 (2주일)\n"
    report += "1. 우선순위 테스트 케이스 구현\n"
    report += "2. 성능 벤치마크 수립\n"
    
    report += "\n---\n*Generated by Multi-Agent Collaboration System*"
    
    state['final_report'] = report
    state['status'] = 'completed'
    
    return state

# 협업 패턴별 워크플로우 생성
def create_sequential_collaboration():
    """순차적 협업 워크플로우"""
    workflow = StateGraph(CollaborationState)
    
    workflow.add_node("security", security_analyzer)
    workflow.add_node("performance", performance_analyzer)
    workflow.add_node("architecture", architecture_reviewer)
    workflow.add_node("testing", test_strategist)
    workflow.add_node("synthesize", synthesizer)
    
    workflow.set_entry_point("security")
    workflow.add_edge("security", "performance")
    workflow.add_edge("performance", "architecture")
    workflow.add_edge("architecture", "testing")
    workflow.add_edge("testing", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()

def create_conditional_collaboration():
    """조건부 협업 워크플로우"""
    workflow = StateGraph(CollaborationState)
    
    def route_after_security(state: CollaborationState) -> str:
        """보안 분석 후 라우팅 결정"""
        if state['collaboration_context'].get('high_risk', False):
            return "architecture"  # 고위험시 아키텍처 먼저
        return "performance"  # 일반적인 경우 성능 분석
    
    workflow.add_node("security", security_analyzer)
    workflow.add_node("performance", performance_analyzer)
    workflow.add_node("architecture", architecture_reviewer)
    workflow.add_node("testing", test_strategist)
    workflow.add_node("synthesize", synthesizer)
    
    workflow.set_entry_point("security")
    
    # 조건부 라우팅
    workflow.add_conditional_edges(
        "security",
        route_after_security,
        {
            "architecture": "architecture",
            "performance": "performance"
        }
    )
    
    workflow.add_edge("performance", "testing")
    workflow.add_edge("architecture", "testing")
    workflow.add_edge("testing", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()

def run_collaboration_analysis(code_path: str, mission: str, pattern: CollaborationPattern):
    """협업 분석 실행"""
    initial_state = CollaborationState(
        code_path=code_path,
        mission=mission,
        pattern=pattern.value,
        agent_results={},
        collaboration_context={},
        decision_points=[],
        final_report="",
        status="started"
    )
    
    # 패턴에 따른 워크플로우 선택
    if pattern == CollaborationPattern.SEQUENTIAL:
        app = create_sequential_collaboration()
    elif pattern == CollaborationPattern.CONDITIONAL:
        app = create_conditional_collaboration()
    else:
        app = create_sequential_collaboration()  # 기본값
    
    # 실행
    final_state = app.invoke(initial_state)
    return final_state

if __name__ == "__main__":
    print("🤝 Agent Collaboration Patterns Demo")
    print("=" * 50)
    
    # 순차적 협업 테스트
    print("\n1️⃣ Sequential Collaboration Pattern")
    result = run_collaboration_analysis(
        code_path="/src/api/payment_service.py",
        mission="Analyze payment service for security, performance, and quality",
        pattern=CollaborationPattern.SEQUENTIAL
    )
    
    print("\n" + result['final_report'])
    
    # 조건부 협업 테스트
    print("\n\n2️⃣ Conditional Collaboration Pattern")
    result2 = run_collaboration_analysis(
        code_path="/src/api/user_service.py",
        mission="Analyze user service with adaptive workflow",
        pattern=CollaborationPattern.CONDITIONAL
    )
    
    with open("collaboration_report.md", "w") as f:
        f.write(result['final_report'])
        f.write("\n\n---\n\n")
        f.write(result2['final_report'])
    
    print("\n✅ 협업 분석 완료!")
    print("📄 보고서 저장됨: collaboration_report.md")
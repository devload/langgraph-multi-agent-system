#!/usr/bin/env python3
"""
LangGraph 워크플로우 텍스트 시각화
실행된 워크플로우를 ASCII 아트로 표현합니다.
"""

from datetime import datetime
from typing import Dict, List, Tuple

def visualize_simple_claude_workflow():
    """단순 Claude 워크플로우 시각화"""
    print("\n" + "="*60)
    print("🔹 Simple Claude Workflow")
    print("="*60)
    print("""
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ CLAUDE  │ ← 코드 분석, 보안 검사, 개선안 제시
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │   END   │
    └─────────┘
    """)

def visualize_multi_agent_parallel():
    """병렬 멀티 에이전트 워크플로우 시각화"""
    print("\n" + "="*60)
    print("🔸 Multi-Agent Parallel Workflow")
    print("="*60)
    print("""
    ┌─────────────┐
    │    START    │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ DISTRIBUTE  │ ← 작업을 5개 에이전트에 분배
    └──────┬──────┘
           │
    ┌──────┴───────┬───────┬───────┬──────┐
    │              │       │       │      │
    ▼              ▼       ▼       ▼      ▼
┌─────────┐  ┌─────────┐ ┌─────┐ ┌─────┐ ┌──────┐
│SECURITY │  │PERFORM. │ │ARCH.│ │TEST │ │ DOC. │
│ AGENT   │  │ AGENT   │ │AGENT│ │AGENT│ │AGENT │
└────┬────┘  └────┬────┘ └──┬──┘ └──┬──┘ └──┬───┘
     │            │         │       │       │
     └────────────┴─────────┴───────┴───────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ SYNTHESIZE  │ ← 결과 통합
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     END     │
                    └─────────────┘
    
    병렬 실행 시간: ~3초 (모든 에이전트 동시 실행)
    """)

def visualize_sequential_collaboration():
    """순차적 협업 워크플로우 시각화"""
    print("\n" + "="*60)
    print("🔹 Sequential Collaboration Workflow")
    print("="*60)
    print("""
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ┌─────────────┐
    │  SECURITY   │ ← 보안 취약점 분석
    │   AGENT     │   결과: 위험도 8.5/10
    └──────┬──────┘
           │ 
           │ 컨텍스트 전달: {high_risk: true, critical_vulns: [...]}
           ▼
    ┌─────────────┐
    │ PERFORMANCE │ ← 성능 분석 + 보안 영향 평가
    │   AGENT     │   결과: 최적화 점수 5.5/10
    └──────┬──────┘
           │
           │ 컨텍스트 전달: {needs_architecture_review: true}
           ▼
    ┌─────────────┐
    │ARCHITECTURE │ ← 구조 검토 + 이전 분석 고려
    │   AGENT     │   결과: 설계 개선안 제시
    └──────┬──────┘
           │
           │ 모든 이슈 전달
           ▼
    ┌─────────────┐
    │   TESTING   │ ← 테스트 전략 수립
    │   AGENT     │   결과: 우선순위 테스트 케이스
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ SYNTHESIZE  │ ← 최종 보고서 생성
    └──────┬──────┘
           │
           ▼
    ┌─────────┐
    │   END   │
    └─────────┘
    """)

def visualize_conditional_routing():
    """조건부 라우팅 워크플로우 시각화"""
    print("\n" + "="*60)
    print("🔸 Conditional Routing Workflow")
    print("="*60)
    print("""
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
         ▼
    ┌─────────────┐
    │  SECURITY   │ ← 보안 분석
    │   AGENT     │
    └──────┬──────┘
           │
           │ 조건 확인: risk_score > 7?
           │
      ┌────┴────┐
      │ 높은 위험 │     낮은 위험
      ▼         │              │
┌──────────┐    │              │
│ARCHITECT │    │              │
│  AGENT   │    │              ▼
└────┬─────┘    │         ┌──────────┐
     │          │         │PERFORMAN.│
     │          │         │  AGENT   │
     │          │         └────┬─────┘
     │          │              │
     └──────────┴──────────────┘
                │
                ▼
         ┌─────────────┐
         │   TESTING   │
         │   AGENT     │
         └──────┬──────┘
                │
                ▼
         ┌─────────────┐
         │ SYNTHESIZE  │
         └──────┬──────┘
                │
                ▼
         ┌─────────┐
         │   END   │
         └─────────┘
    """)

def visualize_execution_trace():
    """실제 실행 추적 시각화"""
    print("\n" + "="*60)
    print("🔍 Execution Trace (실제 실행 경로)")
    print("="*60)
    
    # 실행 로그 시뮬레이션
    execution_log = [
        ("2025-07-25 00:08:00", "START", "미션 시작: 결제 서비스 분석"),
        ("2025-07-25 00:08:01", "DISTRIBUTE", "5개 에이전트에 작업 분배"),
        ("2025-07-25 00:08:01", "PARALLEL", "병렬 실행 시작"),
        ("2025-07-25 00:08:01", "SECURITY", "🔐 SQL Injection 발견"),
        ("2025-07-25 00:08:01", "PERFORMANCE", "⚡ N+1 쿼리 문제 발견"),
        ("2025-07-25 00:08:01", "ARCHITECTURE", "🏗️ SOLID 원칙 위반 발견"),
        ("2025-07-25 00:08:01", "TESTING", "🧪 30% 테스트 커버리지"),
        ("2025-07-25 00:08:01", "DOCUMENTATION", "📚 Docstring 부족"),
        ("2025-07-25 00:08:03", "SYNTHESIZE", "📊 결과 통합 중"),
        ("2025-07-25 00:08:04", "END", "✅ 분석 완료: 15개 이슈 발견")
    ]
    
    print("시간            노드              상태/결과")
    print("-" * 60)
    
    for timestamp, node, status in execution_log:
        time_part = timestamp.split()[1]
        print(f"{time_part}  {node:15} {status}")
    
    print("\n총 실행 시간: 4초")
    print("병렬 처리로 인한 시간 절약: ~12초 (순차 실행 대비)")

def show_workflow_comparison():
    """워크플로우 비교"""
    print("\n" + "="*60)
    print("📊 Workflow Comparison")
    print("="*60)
    print("""
┌─────────────────┬──────────────┬────────────┬─────────────┐
│   Workflow      │ 실행 시간    │ 에이전트 수 │ 장점        │
├─────────────────┼──────────────┼────────────┼─────────────┤
│ Simple Claude   │ 1-2초        │ 1개        │ 빠르고 간단 │
│ Parallel Multi  │ 3초          │ 5개        │ 종합적 분석 │
│ Sequential      │ 5-10초       │ 4-5개      │ 컨텍스트공유│
│ Conditional     │ 3-8초        │ 3-5개      │ 동적 라우팅 │
└─────────────────┴──────────────┴────────────┴─────────────┘
    """)

def show_agent_capabilities():
    """에이전트 능력 매트릭스"""
    print("\n" + "="*60)
    print("🤖 Agent Capabilities Matrix")
    print("="*60)
    print("""
┌─────────────┬────────┬────────┬──────┬────────┬──────┐
│   능력      │Security│Perform.│Arch. │Testing │ Doc. │
├─────────────┼────────┼────────┼──────┼────────┼──────┤
│SQL Injection│   ⭐⭐⭐  │   ⭐    │  ⭐   │   ⭐⭐   │  -   │
│Memory Leaks │   ⭐    │   ⭐⭐⭐  │  ⭐⭐  │   ⭐    │  -   │
│Code Smell   │   ⭐    │   ⭐    │  ⭐⭐⭐ │   ⭐⭐   │  ⭐⭐  │
│Performance  │   -    │   ⭐⭐⭐  │  ⭐   │   ⭐    │  -   │
│Test Coverage│   -    │   -    │  ⭐   │   ⭐⭐⭐  │  ⭐   │
│Documentation│   -    │   -    │  ⭐   │   ⭐    │  ⭐⭐⭐ │
└─────────────┴────────┴────────┴──────┴────────┴──────┘

⭐⭐⭐ = 전문 영역, ⭐⭐ = 보통, ⭐ = 기본, - = 해당없음
    """)

if __name__ == "__main__":
    print("🎨 LangGraph Workflow Visualization")
    print("=" * 60)
    
    # 모든 워크플로우 시각화
    visualize_simple_claude_workflow()
    visualize_multi_agent_parallel()
    visualize_sequential_collaboration()
    visualize_conditional_routing()
    visualize_execution_trace()
    show_workflow_comparison()
    show_agent_capabilities()
    
    print("\n" + "="*60)
    print("💡 핵심 인사이트:")
    print("- 병렬 실행으로 3초 내 5개 에이전트 분석 완료")
    print("- 순차 실행은 에이전트 간 컨텍스트 공유로 심층 분석")
    print("- 조건부 라우팅으로 상황에 맞는 최적 경로 선택")
    print("- 각 에이전트는 전문 분야에 특화된 분석 수행")
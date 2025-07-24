#!/usr/bin/env python3
"""
Claude 전용 코드 리뷰 워크플로우 예제

LangGraph를 사용하여 Claude 에이전트로 코드 리뷰를 수행하는 예제입니다.
Mock LangGraph 구현을 포함하여 외부 의존성 없이 실행 가능합니다.

주요 기능:
- Claude: 코드 분석, 보안 취약점 탐지, 개선사항 제시
- 보고서 생성: 결과 통합 및 Markdown 보고서
"""

from typing import TypedDict, List, Dict, Any
import json
from datetime import datetime

# Mock LangGraph for testing
class StateGraph:
    def __init__(self, state_type):
        self.nodes = {}
        self.edges = {}
        self.conditional_edges = {}
        self.entry = None
        self.state_type = state_type
        
    def add_node(self, name, func):
        self.nodes[name] = func
        
    def add_edge(self, from_node, to_node):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)
        
    def add_conditional_edges(self, from_node, condition_func, routing_map):
        self.conditional_edges[from_node] = (condition_func, routing_map)
        
    def set_entry_point(self, node):
        self.entry = node
        
    def compile(self):
        return CompiledGraph(self)

class CompiledGraph:
    def __init__(self, graph):
        self.graph = graph
        
    def invoke(self, state):
        current_node = self.graph.entry
        
        while current_node != "END":
            if current_node in self.graph.nodes:
                # Execute node
                state = self.graph.nodes[current_node](state)
                
                # Check for conditional edges
                if current_node in self.graph.conditional_edges:
                    condition_func, routing_map = self.graph.conditional_edges[current_node]
                    next_key = condition_func(state)
                    current_node = routing_map.get(next_key, "END")
                # Check for regular edges
                elif current_node in self.graph.edges:
                    current_node = self.graph.edges[current_node][0]
                else:
                    current_node = "END"
            else:
                break
                
        return state

END = "END"

class CodeReviewState(TypedDict):
    """State for code review workflow"""
    code_path: str
    mission: str
    review_type: str  # "security", "performance", "style", "comprehensive"
    claude_analysis: Dict[str, Any]
    final_report: str
    issues_found: List[Dict[str, Any]]
    status: str
    current_step: str

def analyze_with_claude(state: CodeReviewState) -> CodeReviewState:
    """
    Claude 에이전트의 코드 분석 단계
    
    보안 취약점, 성능 문제, 코드 품질 등을 분석하고
    개선사항을 제시합니다.
    
    Args:
        state: 현재 워크플로우 상태
        
    Returns:
        분석 결과가 추가된 상태
    """
    print(f"🔍 Claude analyzing code: {state['code_path']}")
    
    # Simulate Claude's comprehensive analysis
    state['current_step'] = 'claude_analysis'
    state['claude_analysis'] = {
        'timestamp': datetime.now().isoformat(),
        'findings': [
            {
                'type': 'security',
                'severity': 'high',
                'line': 45,
                'issue': 'Potential SQL injection vulnerability',
                'suggestion': 'Use parameterized queries',
                'fix': '''def safe_query(user_input):
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_input,))
    return cursor.fetchall()'''
            },
            {
                'type': 'performance',
                'severity': 'medium',
                'line': 123,
                'issue': 'Inefficient loop with O(n²) complexity',
                'suggestion': 'Consider using a hash map for O(n) lookup',
                'fix': '''# Convert O(n²) to O(n) using dictionary
lookup_dict = {item.id: item for item in items}
for id in search_ids:
    if id in lookup_dict:
        process(lookup_dict[id])'''
            },
            {
                'type': 'maintainability',
                'severity': 'low',
                'issue': 'Missing type hints',
                'suggestion': 'Add type hints for better code documentation',
                'fix': 'def process_data(items: List[Item]) -> Dict[str, Any]:'
            }
        ],
        'overall_quality': 7.5,
        'summary': 'Code has good structure but needs security improvements and performance optimization',
        'refactoring_suggestions': [
            'Extract complex logic into separate functions',
            'Add comprehensive error handling',
            'Implement logging for better debugging'
        ]
    }
    
    # Add findings to issues list
    state['issues_found'].extend(state['claude_analysis']['findings'])
    
    return state

def generate_report(state: CodeReviewState) -> CodeReviewState:
    """Generate final consolidated report"""
    print("📝 Generating final report...")
    
    state['current_step'] = 'report_generation'
    
    # Create comprehensive report
    report = f"""# Code Review Report

**File**: {state['code_path']}  
**Review Type**: {state['review_type']}  
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Reviewer**: Claude AI Assistant

## Executive Summary

{state['claude_analysis']['summary']}

**Overall Quality Score**: {state['claude_analysis']['overall_quality']}/10

## Issues Found ({len(state['issues_found'])} total)

### 🚨 Critical Issues
"""
    
    # Group issues by severity
    critical_issues = [i for i in state['issues_found'] if i.get('severity') == 'high']
    medium_issues = [i for i in state['issues_found'] if i.get('severity') == 'medium']
    low_issues = [i for i in state['issues_found'] if i.get('severity') == 'low']
    
    for issue in critical_issues:
        report += f"\n#### {issue['type'].title()} Issue (Line {issue.get('line', 'N/A')})"
        report += f"\n- **Problem**: {issue['issue']}"
        report += f"\n- **Solution**: {issue['suggestion']}"
        if 'fix' in issue:
            report += f"\n- **Code Fix**:\n```python\n{issue['fix']}\n```"
    
    report += "\n\n### ⚠️  Medium Priority Issues\n"
    for issue in medium_issues:
        report += f"\n#### {issue['type'].title()} Issue"
        report += f"\n- **Problem**: {issue['issue']}"
        report += f"\n- **Solution**: {issue['suggestion']}"
        if 'fix' in issue:
            report += f"\n- **Code Fix**:\n```python\n{issue['fix']}\n```"
    
    report += "\n\n### 💡 Low Priority Issues\n"
    for issue in low_issues:
        report += f"\n- **{issue['type'].title()}**: {issue.get('suggestion', issue.get('issue'))}"
    
    # Add refactoring suggestions
    report += "\n\n## 🔧 Refactoring Suggestions\n"
    for suggestion in state['claude_analysis']['refactoring_suggestions']:
        report += f"\n- {suggestion}"
    
    report += "\n\n## 📋 Next Steps\n"
    report += "1. **Immediate**: Address critical security vulnerabilities\n"
    report += "2. **Short-term**: Implement performance optimizations\n"
    report += "3. **Long-term**: Apply refactoring suggestions for better maintainability\n"
    
    report += "\n\n---\n*Report generated by Claude AI Code Review System*"
    
    state['final_report'] = report
    state['status'] = 'completed'
    
    return state

def create_claude_review_graph():
    """
    Claude 전용 코드 리뷰 워크플로우 그래프 생성
    
    다음 단계로 구성:
    1. analyze_code: Claude가 종합적인 분석 수행
    2. generate_report: 최종 보고서 생성
    
    Returns:
        컴파일된 워크플로우 그래프
    """
    workflow = StateGraph(CodeReviewState)
    
    # Add nodes
    workflow.add_node("analyze_code", analyze_with_claude)
    workflow.add_node("generate_report", generate_report)
    
    # Set entry point
    workflow.set_entry_point("analyze_code")
    
    # Add edges
    workflow.add_edge("analyze_code", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()

def run_code_review(code_path: str, mission: str, review_type: str = "comprehensive"):
    """Run a code review workflow"""
    # Create initial state
    initial_state = CodeReviewState(
        code_path=code_path,
        mission=mission,
        review_type=review_type,
        claude_analysis={},
        final_report="",
        issues_found=[],
        status="started",
        current_step="init"
    )
    
    # Create and run workflow
    app = create_claude_review_graph()
    
    # Execute workflow
    final_state = app.invoke(initial_state)
    
    return final_state

if __name__ == "__main__":
    # Example usage
    result = run_code_review(
        code_path="/src/api/user_handler.py",
        mission="Perform comprehensive code review focusing on security, performance, and maintainability",
        review_type="comprehensive"
    )
    
    print("\n" + "="*50)
    print(result['final_report'])
    
    # Save report
    with open("claude_code_review_report.md", "w") as f:
        f.write(result['final_report'])
    print("\n✅ Report saved to: claude_code_review_report.md")
#!/usr/bin/env python3
"""
실제 취약한 코드를 분석하는 예제
"""

from multi_agent_system import run_multi_agent_analysis
import os

# 실제 파일 경로
sample_code_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "test_samples/vulnerable_payment_service.py"
)

# 파일 내용 읽기
with open(sample_code_path, 'r') as f:
    code_content = f.read()

print("📄 분석할 코드:")
print("=" * 50)
print(f"파일: {sample_code_path}")
print(f"크기: {len(code_content)} bytes")
print(f"라인 수: {len(code_content.splitlines())} lines")
print("=" * 50)
print("\n코드 미리보기 (처음 20줄):")
for i, line in enumerate(code_content.splitlines()[:20], 1):
    print(f"{i:3}: {line}")
print("...\n")

# 멀티 에이전트 분석 실행
print("🚀 멀티 에이전트 분석 시작...")
result = run_multi_agent_analysis(
    code_path=sample_code_path,
    mission="Analyze this payment service code for all security vulnerabilities, performance issues, architectural problems, testing gaps, and documentation needs"
)

# 결과 저장
report_path = "vulnerable_payment_analysis.md"
with open(report_path, "w") as f:
    f.write(result['final_report'])

print(f"\n✅ 분석 완료!")
print(f"📄 상세 보고서: {report_path}")

# 주요 발견사항 요약
print("\n🔍 주요 발견사항:")
print(f"- 총 이슈: {result['total_issues']}개")
print(f"- Critical: {result['severity_summary']['critical']}개")
print(f"- High: {result['severity_summary']['high']}개")
print(f"- Medium: {result['severity_summary']['medium']}개")
print(f"- Low: {result['severity_summary']['low']}개")

# 각 에이전트별 점수
print("\n📊 에이전트별 평가:")
for agent, data in result['agents_results'].items():
    score = data.get('score', 'N/A')
    summary = data.get('summary', 'N/A')
    print(f"- {agent.capitalize()}: {score}/10")
    print(f"  → {summary}")
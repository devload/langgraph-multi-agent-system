# LangGraph Multi-Agent System - 예시 가이드

## 🎯 구현된 예시

### 1. Code Review Graph (examples/code_review_graph.py)
실제 작동하는 LangGraph 워크플로우 예시입니다.

```python
# 실행 방법
python examples/code_review_graph.py
```

**주요 특징:**
- Mock LangGraph 구현 (외부 의존성 없음)
- 상태 기반 워크플로우
- 조건부 라우팅
- Claude → Gemini 순차 처리

**워크플로우:**
```
start → analyze_code (Claude) → enhance_analysis (Gemini) → generate_report → end
```

### 2. Demo Scenarios (examples/demo_scenario.py)
다양한 사용 사례를 보여주는 데모입니다.

```python
# 실행 방법
python examples/demo_scenario.py
```

**포함된 데모:**
1. **Code Review Workflow**: 보안 취약점 및 성능 이슈 분석
2. **Workflow Patterns**: 다양한 워크플로우 패턴
3. **Mission Examples**: 실제 사용 가능한 미션 예시
4. **Real-World Scenario**: API 엔드포인트 보안 감사

### 3. Log Analysis Example (examples/log_analysis_example.py)
실제 시스템과 통합된 로그 분석 예시입니다.

```python
# 시스템 시작 후 실행
./start_production.sh
python examples/log_analysis_example.py
```

## 📋 워크플로우 패턴

### 1. Sequential Analysis (순차 분석)
```json
{
  "workflow": [
    {"from": "start", "to": "claude"},
    {"from": "claude", "to": "gemini"},
    {"from": "gemini", "to": "end"}
  ]
}
```
**용도**: 각 에이전트가 이전 분석을 기반으로 개선

### 2. Single Agent (단일 에이전트)
```json
{
  "workflow": [
    {"from": "start", "to": "claude"},
    {"from": "claude", "to": "end"}
  ]
}
```
**용도**: 특정 에이전트의 기능만 필요한 경우

### 3. Validation Chain (검증 체인)
```json
{
  "workflow": [
    {"from": "start", "to": "claude"},
    {"from": "claude", "to": "gemini"},
    {"from": "gemini", "to": "validator"},
    {"from": "validator", "to": "end"}
  ]
}
```
**용도**: 품질 보증 및 검증이 필요한 경우

## 🎯 실제 미션 예시

### 1. 보안 감사
```python
mission = """Perform a comprehensive security audit:
1. Identify all security vulnerabilities
2. Check for insecure dependencies
3. Review authentication patterns
4. Suggest specific fixes with code examples
5. Prioritize issues by severity"""
```

### 2. 성능 최적화
```python
mission = """Analyze code for performance bottlenecks:
1. Identify inefficient algorithms
2. Find memory leaks
3. Suggest caching strategies
4. Provide optimized alternatives
5. Estimate performance improvements"""
```

### 3. 문서화
```python
mission = """Generate comprehensive documentation:
1. Create function docstrings
2. Generate API documentation
3. Write usage examples
4. Create README
5. Add inline comments"""
```

### 4. 테스트 생성
```python
mission = """Create comprehensive test suite:
1. Write unit tests
2. Create integration tests
3. Add edge case tests
4. Generate test fixtures
5. Set up CI config"""
```

### 5. 리팩토링
```python
mission = """Create refactoring plan:
1. Identify code smells
2. Suggest design patterns
3. Break down monolithic functions
4. Improve code organization
5. Create step-by-step guide"""
```

## 🚀 빠른 시작

### 1. Mock 테스트 (시스템 없이)
```bash
# LangGraph 예시 실행
python examples/code_review_graph.py

# 데모 시나리오 실행
python examples/demo_scenario.py
```

### 2. 전체 시스템 테스트
```bash
# 시스템 시작
./start_production.sh

# 로그 분석 예시 실행
python examples/log_analysis_example.py

# API 직접 호출
curl -X POST http://localhost:8000/api/mission/register \
  -H "Content-Type: application/json" \
  -d @examples/mission_request.json
```

## 📊 테스트 결과

### Code Review 예시 출력
```
🔍 Claude analyzing code: /tmp/demo_code/sample.py
🚀 Gemini enhancing analysis for: /tmp/demo_code/sample.py
📝 Generating final report...

✅ Code review completed!
   Status: completed
   Issues found: 3
   
- SQL Injection vulnerability (Critical)
- O(n²) performance issue (Medium)  
- Missing type hints (Low)
```

### 생성된 보고서 구조
```markdown
# Code Review Report

## Executive Summary
- Overall Quality Score: 7.5/10
- Refactoring Score: 8.2/10

## Issues Found
### Critical Issues
- SQL Injection vulnerability

## Implementation Suggestions
### SQL injection fix
[구체적인 코드 예시]

### Performance optimization  
[최적화된 코드 예시]
```

## 🔧 커스터마이징

### 새로운 워크플로우 추가
```python
def create_custom_workflow():
    workflow = StateGraph(CustomState)
    
    # 노드 추가
    workflow.add_node("preprocess", preprocess_func)
    workflow.add_node("analyze", analyze_func)
    workflow.add_node("postprocess", postprocess_func)
    
    # 엣지 설정
    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "analyze")
    workflow.add_edge("analyze", "postprocess")
    workflow.add_edge("postprocess", END)
    
    return workflow.compile()
```

### 조건부 라우팅
```python
def routing_logic(state):
    if state['severity'] == 'critical':
        return 'urgent_handler'
    else:
        return 'normal_flow'

workflow.add_conditional_edges(
    "analyze",
    routing_logic,
    {
        "urgent_handler": "emergency_response",
        "normal_flow": "standard_process"
    }
)
```

## 📝 다음 단계

1. **예시 실행**: 제공된 예시들을 실행해보세요
2. **커스터마이징**: 자신의 use case에 맞게 수정하세요
3. **새 미션 생성**: 다양한 분석 시나리오를 시도해보세요
4. **워크플로우 확장**: 더 복잡한 워크플로우를 구현해보세요

---

모든 예시는 실제로 작동하며, Mock 구현을 통해 LangGraph 없이도 테스트할 수 있습니다.
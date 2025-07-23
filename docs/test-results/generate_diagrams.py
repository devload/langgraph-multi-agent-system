#!/usr/bin/env python3
"""
Generate visual diagrams for tested workflows
"""

def generate_mermaid_diagrams():
    """Generate all workflow diagrams"""
    
    diagrams = {
        "code_review_workflow": """
# Code Review Workflow (실제 테스트)
```mermaid
graph TD
    start([Start]) --> analyze_code[Claude: Analyze Code]
    analyze_code --> decision{Critical Issues > 3?}
    decision -->|Yes| generate_report[Generate Report]
    decision -->|No| enhance_analysis[Gemini: Enhance Analysis]
    enhance_analysis --> generate_report
    generate_report --> end_node([End])
```

결과:
- SQL Injection 발견 (Line 45)
- O(n²) 성능 이슈
- 타입 힌트 누락
""",

        "mission_execution": """
# Mission Execution Flow (demo123)
```mermaid
sequenceDiagram
    participant Client
    participant Hub
    participant Claude
    participant Gemini
    
    Client->>Hub: Register Mission
    Hub-->>Client: missionId: demo123
    
    Client->>Hub: Run Mission
    Hub->>Claude: Execute Analysis
    Note over Claude: Find security issues<br/>Find performance issues
    Claude-->>Hub: 3 issues found
    
    Hub->>Gemini: Enhance Analysis
    Note over Gemini: Generate fixes<br/>Add recommendations
    Gemini-->>Hub: Solutions provided
    
    Hub-->>Client: Mission Completed
    Hub->>Hub: Generate Report
```
""",

        "tested_patterns": """
# 테스트한 워크플로우 패턴들
```mermaid
graph TD
    subgraph "1. Sequential (실제 사용)"
        A1[Start] --> A2[Claude]
        A2 --> A3[Gemini]
        A3 --> A4[End]
    end
    
    subgraph "2. Single Agent"
        B1[Start] --> B2[Claude]
        B2 --> B3[End]
    end
    
    subgraph "3. Conditional"
        C1[Start] --> C2[Analyze]
        C2 --> C3{Severity?}
        C3 -->|High| C4[Urgent]
        C3 -->|Low| C5[Normal]
        C4 --> C6[End]
        C5 --> C6
    end
```
""",

        "data_flow": """
# 데이터 흐름도
```mermaid
graph LR
    subgraph "Input"
        code[Source Code]
        logs[System Logs]
    end
    
    subgraph "Processing"
        claude[Claude Analysis]
        gemini[Gemini Enhancement]
    end
    
    subgraph "Output"
        issues[Issues Found]
        fixes[Code Fixes]
        report[Final Report]
    end
    
    code --> claude
    logs --> claude
    claude --> issues
    issues --> gemini
    gemini --> fixes
    fixes --> report
    
    style code fill:#FFFACD
    style logs fill:#FFFACD
    style claude fill:#87CEEB
    style gemini fill:#DDA0DD
    style report fill:#98FB98
```
""",

        "system_state": """
# 시스템 상태 다이어그램
```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Registered: POST /register
    Registered --> Running: POST /run
    
    state Running {
        [*] --> Claude_Processing
        Claude_Processing --> Gemini_Processing
        Gemini_Processing --> [*]
    }
    
    Running --> Completed: Success
    Running --> Failed: Error
    
    Completed --> [*]
    Failed --> [*]
    
    note right of Claude_Processing : SQL Injection found<br/>Performance issues<br/>3 total issues
    note right of Gemini_Processing : Parameterized queries<br/>O(n) optimization<br/>Type hints added
```
"""
    }
    
    return diagrams

def print_ascii_workflow():
    """Print ASCII representation of workflow"""
    print("""
실제 테스트한 워크플로우:

1. Code Review Workflow:
   ┌─────────┐     ┌─────────────┐     ┌──────────────┐     ┌────────┐
   │  START  │────▶│   CLAUDE    │────▶│    GEMINI    │────▶│  END   │
   └─────────┘     └─────────────┘     └──────────────┘     └────────┘
                   │ SQL Injection │    │ Fix: Parameterized │
                   │ O(n²) Loop    │    │ Fix: Use Dict O(n) │
                   │ No Type Hints │    │ Fix: Add Types     │

2. Mission Execution (demo123):
   ┌──────────┐
   │ Register │ ──── missionId: demo123
   └────┬─────┘
        │
   ┌────▼─────┐
   │   Run    │ ──── Status: running
   └────┬─────┘
        │
   ┌────▼─────┐
   │  Claude  │ ──── 3 issues found
   └────┬─────┘      - Security (Critical)
        │             - Performance (Medium)
   ┌────▼─────┐      - Maintainability (Low)
   │  Gemini  │ ──── Solutions provided
   └────┬─────┘      - Safe query example
        │             - Dict optimization
   ┌────▼─────┐      - Type hints
   │ Complete │ ──── Report generated
   └──────────┘

3. 테스트 결과:
   ✅ Mock LangGraph 작동
   ✅ 상태 기반 워크플로우
   ✅ 조건부 라우팅
   ✅ 멀티 에이전트 협업
   ✅ 자동 보고서 생성
""")

def main():
    """Generate and display all diagrams"""
    print("🎨 LangGraph 워크플로우 시각화")
    print("=" * 60)
    
    # Generate Mermaid diagrams
    diagrams = generate_mermaid_diagrams()
    
    # Save each diagram
    for name, content in diagrams.items():
        filename = f"diagram_{name}.md"
        with open(filename, "w") as f:
            f.write(content)
        print(f"✅ Generated: {filename}")
    
    # Print ASCII workflow
    print("\n" + "=" * 60)
    print_ascii_workflow()
    
    print("\n📊 시각화 요약:")
    print("1. Code Review: 3개 이슈 발견 → 해결책 생성")
    print("2. Mission demo123: 로그 분석 → 보안 위협 탐지")
    print("3. 워크플로우 패턴: Sequential, Single, Conditional")
    print("4. 데이터 흐름: Input → Processing → Output")
    print("5. 상태 관리: Idle → Registered → Running → Completed")

if __name__ == "__main__":
    main()
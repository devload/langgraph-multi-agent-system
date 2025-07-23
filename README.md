# 🤖 LangGraph Multi-Agent System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LangGraph 기반 멀티 에이전트 오케스트레이션 시스템입니다. Claude와 Gemini 같은 여러 AI 에이전트를 워크플로우로 연결하여 복잡한 작업을 수행합니다.

## 🌟 주요 기능

- **🔀 워크플로우 기반 실행**: LangGraph를 사용한 유연한 에이전트 체인
- **🤝 멀티 에이전트 협업**: Claude와 Gemini의 강점을 결합
- **📊 실시간 모니터링**: 미션 상태 추적 및 결과 시각화
- **🔧 확장 가능한 구조**: 새로운 에이전트 쉽게 추가 가능
- **📝 자동 보고서 생성**: Markdown 형식의 종합 보고서

## 🏗️ 시스템 아키텍처

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│     Hub      │────▶│   Agents    │
│   (API)     │     │ (LangGraph)  │     │(Claude/Gem) │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.11 이상
- Claude CLI (선택사항)
- Gemini CLI (선택사항)

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/langgraph-multi-agent-system.git
cd langgraph-multi-agent-system

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 실행

```bash
# 프로덕션 모드로 시작
./docs/start_production.sh

# API 문서 확인
open http://localhost:8000/docs
```

## 📚 사용 예제

### 1. 코드 리뷰 워크플로우

```python
# Mock 버전으로 즉시 테스트 가능
python examples/code_review_graph.py
```

### 2. 미션 등록 및 실행

```bash
# 미션 등록
curl -X POST http://localhost:8000/api/mission/register \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": [
      {"from": "start", "to": "claude"},
      {"from": "claude", "to": "gemini"},
      {"from": "gemini", "to": "end"}
    ],
    "mission": "Analyze this code for security vulnerabilities"
  }'

# 미션 실행
curl -X POST http://localhost:8000/api/mission/{mission_id}/run
```

## 📁 프로젝트 구조

```
.
├── hub/                    # 중앙 오케스트레이션 서버
│   ├── app.py             # FastAPI 애플리케이션
│   ├── flow_template.py   # LangGraph 템플릿 생성
│   └── mission_history.py # 미션 기록 관리
├── agent-claude/          # Claude 에이전트
│   └── claude_agent.py    # Claude CLI 통합
├── agent-gemini/          # Gemini 에이전트
│   └── gemini_agent.py    # Gemini CLI 통합
├── examples/              # 실행 가능한 예제
│   ├── code_review_graph.py
│   └── log_analysis_example.py
└── docs/                  # 문서 및 가이드
```

## 🎯 사용 사례

### 코드 리뷰 자동화
- 보안 취약점 분석
- 성능 최적화 제안
- 코드 품질 개선

### 로그 분석
- 에러 패턴 식별
- 근본 원인 분석
- 해결책 제시

### 문서 생성
- API 문서 자동 생성
- 코드 주석 추가
- README 작성

## 🔧 워크플로우 패턴

### Sequential (순차 처리)
```json
[
  {"from": "start", "to": "claude"},
  {"from": "claude", "to": "gemini"},
  {"from": "gemini", "to": "end"}
]
```

### Single Agent (단일 에이전트)
```json
[
  {"from": "start", "to": "claude"},
  {"from": "claude", "to": "end"}
]
```

### Conditional (조건부 라우팅)
```python
# 심각도에 따라 다른 경로로 분기
if severity == "critical":
    return "urgent_handler"
else:
    return "normal_flow"
```

## 📊 모니터링

웹 대시보드를 통해 실시간으로 미션 상태를 모니터링할 수 있습니다:

```bash
open monitoring/dashboard.html
```

## 🛠️ 개발

### 새 에이전트 추가

1. `agent_base.py`를 상속받아 새 에이전트 클래스 생성
2. `_build_command` 메서드 구현
3. 설정 파일 작성 (`agent_config.yaml`)

```python
class NewAgent(AgentBase):
    def _build_command(self, mission: str) -> list:
        return ["new-cli", "-p", mission]
```

### 테스트

```bash
# 단위 테스트
python -m pytest tests/

# 통합 테스트
python docs/test-results/test_integration.py
```

## 📝 API 문서

전체 API 문서는 FastAPI의 자동 문서 생성 기능을 통해 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

주요 엔드포인트:
- `POST /api/mission/register` - 새 미션 등록
- `POST /api/mission/{id}/run` - 미션 실행
- `GET /api/mission/{id}/status` - 상태 조회
- `GET /api/mission/{id}/results` - 결과 조회

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 개발팀

- 프로젝트 리드: [Your Name]
- 기여자: [Contributors]

## 📞 문의

- 이슈: [GitHub Issues](https://github.com/yourusername/langgraph-multi-agent-system/issues)
- 이메일: your.email@example.com

---

**주의**: 이 시스템을 사용하기 위해서는 Claude와 Gemini CLI가 설치되어 있어야 합니다. Mock 모드로도 테스트 가능합니다.
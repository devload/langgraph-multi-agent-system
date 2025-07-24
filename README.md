# 🤖 LangGraph Multi-Agent System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LangGraph 기반 Claude 에이전트 오케스트레이션 시스템입니다. Claude CLI를 활용하여 코드 리뷰, 분석, 문서 생성 등의 작업을 자동화합니다. 고정된 프롬프트 형식과 파일 기반 통신을 통해 안정적인 AI 작업 실행을 보장합니다.

## 🌟 주요 기능

- **🔀 워크플로우 기반 실행**: LangGraph를 사용한 유연한 에이전트 체인
- **🤖 Claude CLI 통합**: 고정 프롬프트 형식으로 안정적인 실행
- **📁 파일 기반 통신**: mission.md, agentInfo.md, result.md 표준화
- **📊 실시간 모니터링**: 미션 상태 추적 및 결과 시각화
- **🔧 확장 가능한 구조**: 새로운 에이전트 쉽게 추가 가능
- **📝 자동 보고서 생성**: Markdown 형식의 종합 보고서
- **🚀 병렬 처리**: 여러 에이전트 동시 실행 지원

## 🏗️ 시스템 아키텍처

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│     Hub      │────▶│   Agents    │
│   (API)     │     │ (LangGraph)  │     │  (Claude)   │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                    │
                            ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  Mission DB  │     │ Claude CLI  │
                    └──────────────┘     └─────────────┘
```

### 통신 플로우
1. **Mission 등록**: 클라이언트가 Hub에 워크플로우와 미션 전송
2. **Agent 호출**: Hub가 해당 Agent에 미션 전달
3. **파일 생성**: Agent가 mission.md와 agentInfo.md 생성
4. **CLI 실행**: 고정 프롬프트로 Claude CLI 호출
5. **결과 생성**: Claude가 result.md 작성 및 추가 파일 생성
6. **Callback**: Agent가 Hub로 완료 알림

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.11 이상
- Claude CLI (필수) - [설치 가이드](https://claude.ai/code)
- 최소 2GB RAM
- 디스크 공간 1GB 이상

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/langgraph-multi-agent-system.git
cd langgraph-multi-agent-system

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경 설정
cp .env.example .env
# 필요시 .env 파일 수정

# 5. Claude CLI 설치 확인
claude --version
# 설치되어 있지 않다면: https://claude.ai/code
```

### 실행

#### 개별 서비스 실행

```bash
# 1. Hub 서버 시작 (터미널 1)
cd hub
python3 app.py
# Hub가 http://localhost:8000 에서 실행됨

# 2. Claude Agent 시작 (터미널 2)
cd agent-claude
python3 claude_agent.py
# Agent가 http://localhost:8001 에서 실행됨
```

#### 스크립트로 한번에 실행

```bash
# 모든 서비스 시작
./start_all.sh

# API 문서 확인
open http://localhost:8000/docs
```

## 📚 사용 예제

### 1. 간단한 미션 실행

```python
import httpx
import asyncio

async def simple_mission():
    async with httpx.AsyncClient() as client:
        # 미션 등록
        response = await client.post(
            "http://localhost:8000/api/mission/register",
            json={
                "workflow": [
                    {"from": "start", "to": "claude"},
                    {"from": "claude", "to": "end"}
                ],
                "mission": "Python으로 Hello World 함수를 작성해주세요."
            }
        )
        
        mission_id = response.json()["missionId"]
        print(f"Mission ID: {mission_id}")
        
        # 미션 실행
        await client.post(f"http://localhost:8000/api/mission/{mission_id}/run")
        
        # 결과 확인 (30초 후)
        await asyncio.sleep(30)
        results = await client.get(f"http://localhost:8000/api/mission/{mission_id}/results")
        print(results.json())

asyncio.run(simple_mission())
```

### 2. 코드 분석 미션

```bash
# 코드 분석 미션 등록
curl -X POST http://localhost:8000/api/mission/register \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": [
      {"from": "start", "to": "claude"},
      {"from": "claude", "to": "end"}
    ],
    "mission": "다음 Python 코드를 분석하고 개선점을 제시해주세요:\n\ndef process_data(data):\n    result = []\n    for i in range(len(data)):\n        if data[i] % 2 == 0:\n            result.append(data[i] * 2)\n    return result"
  }'

# 응답 예시
# {"missionId": "a1b2c3d4", "status": "registered"}

# 미션 실행
curl -X POST http://localhost:8000/api/mission/a1b2c3d4/run

# 상태 확인
curl http://localhost:8000/api/mission/a1b2c3d4/status

# 결과 조회
curl http://localhost:8000/api/mission/a1b2c3d4/results
```

## 📁 프로젝트 구조

```
.
├── hub/                    # 중앙 오케스트레이션 서버
│   ├── app.py             # FastAPI 애플리케이션
│   ├── flow_template.py   # LangGraph 템플릿 생성
│   └── mission_history.py # 미션 기록 관리
├── agent-claude/          # Claude 에이전트
│   ├── claude_agent.py    # Claude CLI 통합
│   └── agent_config.yaml  # 에이전트 설정
├── agent_base.py          # 에이전트 베이스 클래스
├── examples/              # 실행 가능한 예제
│   ├── multi_agent_system.py     # 멀티 에이전트 예제
│   ├── agent_collaboration.py    # 에이전트 협업 패턴
│   └── visualize_workflows.py    # 워크플로우 시각화
├── test_samples/          # 테스트용 샘플 코드
├── requirements.txt       # Python 의존성
└── .env.example          # 환경 설정 예제
```

### 작업 디렉토리 구조

각 미션은 다음과 같은 파일 구조를 생성합니다:

```
/tmp/claude-workspace/{mission_id}/
├── mission.md              # 미션 내용
├── agentInfo.md           # 콜백 정보 및 메타데이터
├── result.md              # Claude가 생성한 분석 결과
├── claude_execution_result.md  # 실행 로그
└── [생성된 파일들]         # Claude가 생성한 추가 파일
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

## 🔧 고급 설정

### Claude Agent 설정 (agent_config.yaml)

```yaml
agent:
  name: "claude"
  type: "claude-cli"
  timeout: 300  # 최대 실행 시간 (초)
  
cli:
  command: "claude"
  args:
    - "--print"                      # 비대화형 모드
    - "--dangerously-skip-permissions"  # 권한 자동 승인
    - "--allowedTools"
    - "Bash"                         # Bash 명령 실행 허용
  prompt_prefix: "-p"
  
files:
  mission_file: "mission.md"
  result_file: "result.md"
  workspace_dir: "/tmp/claude-workspace"
```

### 고정 프롬프트 형식

Claude Agent는 다음 고정 프롬프트를 사용합니다:

```
mission.md 파일을 읽고, 처리한 뒤에 결과를 result.md에 저장하고 agentInfo.md의 agentCallbackUrl을 호출해주세요.
```

이를 통해 일관된 실행과 예측 가능한 결과를 보장합니다.

## 📊 모니터링 및 로그

### API 엔드포인트

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Agent Health**: http://localhost:8001/health

### 로그 파일

```bash
# Hub 로그
tail -f hub.log

# Claude Agent 로그
tail -f claude_agent.log
```

### 미션 상태 확인

```bash
# 모든 미션 목록
curl http://localhost:8000/api/missions

# 특정 미션 상태
curl http://localhost:8000/api/mission/{mission_id}/status

# 미션 이력
curl http://localhost:8000/api/mission/{mission_id}/history
```

## 🧪 테스트

### 직접 Agent 테스트

```bash
# Claude Agent 직접 호출 테스트
python3 test_direct.py
```

### 통합 테스트

```bash
# 전체 시스템 통합 테스트
python3 test_integration.py

# 멀티 에이전트 테스트
python3 examples/multi_agent_system.py
```

### 성능 테스트

```bash
# 병렬 미션 실행 테스트
python3 test_parallel.py
```

## 📝 주요 API 엔드포인트

### Hub API

| 메소드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/api/mission/register` | 새 미션 등록 |
| POST | `/api/mission/{id}/run` | 미션 실행 |
| GET | `/api/mission/{id}/status` | 미션 상태 조회 |
| GET | `/api/mission/{id}/results` | 미션 결과 조회 |
| GET | `/api/mission/{id}/results/{agent}` | 특정 에이전트 결과 |
| GET | `/api/missions` | 전체 미션 목록 |
| GET | `/api/mission/{id}/history` | 미션 실행 이력 |
| POST | `/api/agent/result` | 에이전트 결과 콜백 |

### Agent API

| 메소드 | 엔드포인트 | 설명 |
|--------|------------|------|
| POST | `/api/agent/command` | 에이전트에 명령 전송 |
| GET | `/health` | 에이전트 상태 확인 |

## 🚀 실제 사용 예시

### 1. 코드 리뷰 자동화

```python
# 보안 취약점 분석
mission = """다음 코드의 보안 취약점을 분석해주세요:
- SQL Injection
- XSS
- 인증/인가 문제
- 민감 정보 노출
"""
```

### 2. 문서 생성

```python
# API 문서 자동 생성
mission = "FastAPI 엔드포인트를 분석하고 OpenAPI 스펙에 맞는 문서를 생성해주세요."
```

### 3. 테스트 코드 생성

```python
# 단위 테스트 생성
mission = "주어진 함수에 대한 pytest 기반 단위 테스트를 작성해주세요."
```

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

## ⚠️ 주의사항

- Claude CLI가 반드시 설치되어 있어야 합니다
- API 키 사용량에 주의하세요 (Claude API 요금 발생)
- 민감한 정보가 포함된 코드는 주의해서 처리하세요
- 작업 공간은 `/tmp/claude-workspace`에 생성됩니다

## 🔍 문제 해결

### Claude CLI 실행 오류
```bash
# 권한 문제 해결
claude --dangerously-skip-permissions
```

### 포트 충돌
```bash
# 기존 프로세스 확인 및 종료
lsof -i :8000
lsof -i :8001
```

### 타임아웃 문제
```yaml
# agent_config.yaml에서 timeout 증가
agent:
  timeout: 600  # 10분으로 증가
```

---

**Made with ❤️ using Claude and LangGraph**
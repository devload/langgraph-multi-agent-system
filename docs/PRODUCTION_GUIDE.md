# Multi-Agent Mission System - Production Guide

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Client/API    │────▶│    Hub Server    │────▶│     Agents      │
│                 │     │  (LangGraph)     │     │ (Claude/Gemini) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
    Mission Request      SQLite Database            CLI Execution
                         Mission History            Result Files
```

## 📋 구성 요소

### 1. Hub Server (hub/)
- **FastAPI 기반 중앙 컨트롤러**
- LangGraph로 워크플로우 관리
- 미션 상태 추적 및 히스토리 관리
- RESTful API 제공

### 2. Agent Services
- **Claude Agent**: Claude CLI 통합
- **Gemini Agent**: Gemini CLI 통합
- 자동 컨텍스트 전달 및 결과 통합

### 3. Mission History
- SQLite 기반 영구 저장소
- 실행 로그 및 통계
- 보고서 생성 기능

## 🚀 프로덕션 배포

### 1. 환경 설정
```bash
# .env 파일 생성
cp .env.example .env

# 필요에 따라 .env 편집
vim .env
```

### 2. 시스템 시작
```bash
# 프로덕션 모드로 시작
./start_production.sh

# 로그 확인
tail -f logs/*.log
```

### 3. 시스템 종료
```bash
./stop_production.sh
```

## 🔧 API 사용법

### 미션 등록
```bash
curl -X POST http://localhost:8000/api/mission/register \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": [
      {"from": "start", "to": "claude"},
      {"from": "claude", "to": "gemini"},
      {"from": "gemini", "to": "end"}
    ],
    "mission": "Analyze the error logs and provide solutions"
  }'
```

### 미션 실행
```bash
curl -X POST http://localhost:8000/api/mission/{mission_id}/run
```

### 상태 확인
```bash
curl http://localhost:8000/api/mission/{mission_id}/status
```

### 결과 조회
```bash
# 모든 에이전트 결과
curl http://localhost:8000/api/mission/{mission_id}/results

# 특정 에이전트 결과
curl http://localhost:8000/api/mission/{mission_id}/results/claude
```

### 미션 히스토리
```bash
# 전체 히스토리 및 로그
curl http://localhost:8000/api/mission/{mission_id}/history

# 마크다운 보고서
curl http://localhost:8000/api/mission/{mission_id}/report
```

### 통계 조회
```bash
curl http://localhost:8000/api/stats
```

## 📊 모니터링

### 웹 대시보드
브라우저에서 `monitoring/dashboard.html` 열기
- 실시간 통계
- 미션 상태 모니터링
- 에이전트 성능 지표

### API 문서
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔒 보안 설정

### API 키 인증 활성화
```bash
# .env 파일에서
ENABLE_AUTH=true
API_KEY=your-secure-api-key

# API 호출 시
curl -H "Authorization: Bearer your-secure-api-key" \
  http://localhost:8000/api/mission/register
```

## 🏃 워크플로우 예시

### 1. 단순 분석
```json
{
  "workflow": [
    {"from": "start", "to": "claude"},
    {"from": "claude", "to": "end"}
  ],
  "mission": "Analyze this code and suggest improvements"
}
```

### 2. 다단계 처리
```json
{
  "workflow": [
    {"from": "start", "to": "claude"},
    {"from": "claude", "to": "gemini"},
    {"from": "gemini", "to": "end"}
  ],
  "mission": "First analyze with Claude, then enhance with Gemini"
}
```

### 3. 병렬 처리 (향후 지원)
```json
{
  "workflow": [
    {"from": "start", "to": "claude"},
    {"from": "start", "to": "gemini"},
    {"from": "claude", "to": "merge"},
    {"from": "gemini", "to": "merge"},
    {"from": "merge", "to": "end"}
  ]
}
```

## 📁 디렉토리 구조
```
multiAgentWorkspace/
├── hub/                      # Hub 서버
│   ├── app.py               # FastAPI 애플리케이션
│   ├── flow_template.py     # LangGraph 템플릿
│   ├── mission_history.py   # 히스토리 관리
│   ├── security.py          # 보안 미들웨어
│   └── missions/            # 미션 데이터
├── agent-claude/            # Claude 에이전트
│   ├── claude_agent.py      # 에이전트 구현
│   └── agent_config.yaml    # 설정
├── agent-gemini/            # Gemini 에이전트
│   ├── gemini_agent.py      # 에이전트 구현
│   └── agent_config.yaml    # 설정
├── monitoring/              # 모니터링 도구
│   └── dashboard.html       # 웹 대시보드
├── logs/                    # 로그 파일
├── venv/                    # Python 가상환경
└── *.sh                     # 실행 스크립트
```

## 🐛 문제 해결

### 서비스가 시작되지 않음
```bash
# 포트 확인
lsof -i :8000
lsof -i :8001
lsof -i :8002

# 로그 확인
tail -f logs/hub.log
tail -f logs/claude-agent.log
```

### CLI 실행 실패
```bash
# CLI 경로 확인
which claude
which gemini

# .env에서 경로 업데이트
CLAUDE_CLI_PATH=/path/to/claude
GEMINI_CLI_PATH=/path/to/gemini
```

### 데이터베이스 오류
```bash
# 데이터베이스 재생성
rm hub/missions.db
./start_production.sh
```

## 🔄 업그레이드

1. 코드 업데이트
2. 서비스 중지: `./stop_production.sh`
3. 종속성 업데이트: `pip install -r requirements.txt`
4. 서비스 재시작: `./start_production.sh`

## 📈 성능 튜닝

### 환경 변수 조정
- `MAX_CONCURRENT_MISSIONS`: 동시 실행 미션 수
- `MISSION_TIMEOUT`: 전체 미션 타임아웃
- `AGENT_TIMEOUT`: 개별 에이전트 타임아웃

### 리소스 모니터링
```bash
# CPU/메모리 사용량
htop

# 디스크 사용량
df -h /tmp/agent-workspaces
```

## 🤝 기여하기

1. 이슈 생성
2. 기능 브랜치 생성
3. 테스트 추가
4. PR 제출

---

**Version**: 1.0.0  
**Last Updated**: 2025-01-23
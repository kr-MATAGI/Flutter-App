# AI Chat Backend API

LangGraph와 LlamaIndex를 활용한 FastAPI 기반의 AI 채팅 백엔드 API 서버입니다.

## 주요 기능

- **LangGraph 기반 AI 에이전트**
  - 다중 노드 처리 (Main, DB Query, Evaluation)
  - 상태 기반 대화 관리
  - 품질 평가 및 피드백 시스템

- **RAG (Retrieval Augmented Generation)**
  - ChromaDB 기반 벡터 저장소
  - 문서 임베딩 및 검색
  - 컨텍스트 기반 응답 생성

- **다중 LLM 지원**
  - OpenAI GPT-4
  - Llama 3.1
  - Claude (예정)
  - Gemini (예정)

## 기술 스택

- **Backend Framework**: FastAPI
- **Vector Database**: ChromaDB
- **LLM Framework**: 
  - LangGraph (대화 흐름 제어)
  - LlamaIndex (RAG 구현)
- **Language Models**:
  - OpenAI API
  - Ollama

## 프로젝트 구조

```
fastapi_app/
├── app/
│   ├── core/              # 핵심 설정 및 유틸리티
│   │   ├── config.py     # 환경 설정
│   │   └── ...
│   │
│   ├── models/           # 데이터 모델
│   │   ├── graph_state.py    # LangGraph 상태 모델
│   │   └── ...
│   │
│   ├── prompts/          # 프롬프트 템플릿
│   │   ├── main_model.yaml   # 메인 모델 프롬프트
│   │   ├── eval_node.yaml    # 평가 노드 프롬프트
│   │   └── db_query.yaml     # DB 쿼리 프롬프트
│   │
│   ├── routers/          # API 라우터
│   │   ├── controller/   # 컨트롤러
│   │   │   ├── agent_ctl.py  # AI 에이전트 컨트롤러
│   │   │   ├── rag_ctl.py    # RAG 컨트롤러
│   │   │   └── ...
│   │   └── ws_chat.py    # WebSocket 채팅 라우터
│   │
│   ├── utils/            # 유틸리티
│   │   ├── logger.py     # 로깅 설정
│   │   └── ...
│   │
│   └── main.py          # 애플리케이션 진입점
│
├── tests/               # 테스트 코드
├── .env                # 환경 변수
└── requirements.txt    # 의존성 패키지
```

## 설치 방법

1. Python 3.11 이상이 필요합니다.

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정:
```bash
cp .env.example .env
# .env 파일을 열어 필요한 API 키와 설정을 입력
```

## 실행 방법

개발 서버 실행:
```bash
uvicorn app.main:app --reload
```

서버는 기본적으로 http://localhost:8000 에서 실행됩니다.

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 아키텍처

이 프로젝트는 다음과 같은 아키텍처를 사용합니다:

1. **LangGraph 기반 대화 관리**
   - 상태 기반 대화 흐름 제어
   - 다중 노드 간 라우팅
   - 품질 평가 및 피드백 루프

2. **RAG 시스템**
   - ChromaDB 기반 벡터 저장소
   - 문서 임베딩 및 검색
   - 컨텍스트 기반 응답 생성

3. **WebSocket 기반 실시간 통신**
   - 비동기 대화 처리
   - 스트리밍 응답 지원

## 라이선스

MIT License 
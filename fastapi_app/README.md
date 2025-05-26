# AI Chat Backend API

FastAPI 기반의 AI 채팅 백엔드 API 서버입니다.

## 설치 방법

1. Python 3.8 이상이 필요합니다.

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
- `.env.example` 파일을 복사하여 `.env` 파일 생성
- 필요한 환경 변수 값 설정 (API 키 등)

## 실행 방법

개발 서버 실행:
```bash
uvicorn app.main:app --reload
```

서버는 기본적으로 http://localhost:8000 에서 실행됩니다.

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 기능

- AI 채팅
- 사용자 인증
- 채팅 기록 관리

## 프로젝트 구조

```
fastapi_app/
├── app/
│   ├── core/          # 설정 및 유틸리티
│   ├── models/        # 데이터베이스 모델
│   ├── routers/       # API 라우터
│   ├── schemas/       # Pydantic 모델
│   └── main.py       # 애플리케이션 진입점
├── tests/            # 테스트 코드
├── .env             # 환경 변수
└── requirements.txt  # 의존성 패키지
``` 
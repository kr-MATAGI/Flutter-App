# AI 채팅 애플리케이션 🤖

FastAPI와 Flutter를 사용한 실시간 AI 채팅 애플리케이션입니다.

## 주요 기능 ✨

- OpenAI GPT를 활용한 AI 채팅
- 실시간 1:1 채팅
- 채팅 이력 저장 및 조회
- 사용자 인증 시스템
- 실시간 메시지 알림

## 기술 스택 🛠

### 백엔드
- [FastAPI](https://fastapi.tiangolo.com/) - 고성능 Python 웹 프레임워크
- [PostgreSQL](https://www.postgresql.org/) - 메인 데이터베이스
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 데이터 검증
- [OpenAI API](https://openai.com/) - AI 채팅 엔진
- [WebSocket](https://websockets.readthedocs.io/) - 실시간 통신

### 프론트엔드
- [Flutter](https://flutter.dev/) - 크로스 플랫폼 UI 프레임워크
- [Provider](https://pub.dev/packages/provider) - 상태 관리
- [dio](https://pub.dev/packages/dio) - HTTP 클라이언트

## 시작하기 🚀

### 사전 요구사항
- Python 3.11+
- PostgreSQL
- Flutter SDK
- OpenAI API 키

### 백엔드 설정

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경변수 설정
```bash
cp .env.example .env
# .env 파일을 수정하여 필요한 설정 추가
```

4. 데이터베이스 마이그레이션
```bash
alembic upgrade head
```

5. 서버 실행
```bash
uvicorn app.main:app --reload
```

### API 문서
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 데이터베이스 스키마 📊

### chat_log 테이블
| 컬럼 | 타입 | 설명 |
|------|------|------|
| idx | BIGINT | 기본 키 |
| user_idx | BIGINT | 사용자 ID |
| message | TEXT | 사용자 메시지 |
| add_time | TIMESTAMPTZ | 메시지 작성 시간 |
| room_id | BIGINT | 채팅방 ID |
| response_chat | TEXT | AI 응답 메시지 |

## API 엔드포인트 🌐

### 채팅
- `POST /api/v1/chat` - 새 메시지 전송
- `GET /api/v1/chat/history/{room_id}` - 채팅 이력 조회
- `WS /api/v1/chat/ws/{room_id}/{user_id}` - 실시간 채팅 연결

### 인증
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/register` - 회원가입

## 라이선스 📝

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여하기 🤝

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

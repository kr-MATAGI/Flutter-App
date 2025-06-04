from pydantic import BaseModel
from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


# Pydantic 모델 - API 요청/응답용
class ChatRequest(BaseModel):
    user_id: str
    message: str
    room_id: str


class ChatResponse(BaseModel):
    status: str
    user_id: str
    message: str
    room_id: str

    class Config:
        from_attributes = True


# SQLAlchemy 모델 - 데이터베이스용
class DB_ChatLog(Base):
    __tablename__ = "chat_log"

    idx = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    add_time = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    room_id = Column(Text, nullable=False)
    response_chat = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "idx": self.idx,
            "user_id": self.user_idx,
            "message": self.message,
            "add_time": self.add_time.isoformat() if self.add_time else None,
            "room_id": self.room_id,
            "response_chat": self.response_chat,
        }

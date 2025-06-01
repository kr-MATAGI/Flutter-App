from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KafkaMessage(BaseModel):
    """Kafka 메시지 모델"""

    message_id: str = Field(..., description="메시지 고유 ID")
    sender_id: str = Field(..., description="발신자 ID")
    receiver_id: str = Field(..., description="수신자 ID")
    content: str = Field(..., description="메시지 내용")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="메시지 전송 시간"
    )
    chat_room_id: Optional[str] = Field(None, description="채팅방 ID")
    message_type: str = Field(
        default="text", description="메시지 타입 (text, image, file 등)"
    )
    status: str = Field(
        default="sent", description="메시지 상태 (sent, delivered, read 등)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_123456",
                "sender_id": "user_123",
                "receiver_id": "user_456",
                "content": "안녕하세요!",
                "timestamp": "2024-02-28T12:00:00Z",
                "chat_room_id": "room_789",
                "message_type": "text",
                "status": "sent",
            }
        }

from pydantic import BaseModel


class KafkaMessage(BaseModel):
    user_id: str
    message: str
    type: str  # ai_chat: AI챗, human_chat: 일반챗

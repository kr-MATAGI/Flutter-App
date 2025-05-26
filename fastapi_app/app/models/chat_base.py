from pydantic import BaseModel


class ChatMessage(BaseModel):
    user_id: str
    message: str
    room_id: str
    timestamp: str
    status: str


class ChatResponse(BaseModel):
    status: str
    message_id: str
    user_id: str
    message: str
    room_id: str
    timestamp: str
    status: str

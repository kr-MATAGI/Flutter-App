from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr


class ImageScanRequest(BaseModel):
    user_id: str
    store_name: str

    class Config:
        json_schema_extra = {
            "example": {"user_id": "user123", "store_name": "맛있는 식당"}
        }

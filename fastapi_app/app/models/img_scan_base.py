from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr


class ImageScanRequest(BaseModel):
    user_id: Optional[str] = None
    store_name: Optional[str] = None

    @classmethod
    def as_form(cls, user_id: str, store_name: str):
        return cls(user_id=user_id, store_name=store_name)

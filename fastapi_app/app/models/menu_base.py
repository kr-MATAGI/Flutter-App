from pydantic import BaseModel
from typing import List, Any, Optional


class MenuInfo(BaseModel):
    user_id: str
    store_name: str
    file_name: str
    menu_name: str
    cost: int


class MenuImage(BaseModel):
    user_id: str
    file_name: str
    menu_name: str
    cost: int

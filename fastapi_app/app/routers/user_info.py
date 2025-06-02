from fastapi import (
    APIRouter,
    HTTPException,
)

from app.routers.controller.db_ctl import DBController

router = APIRouter()
db_controller = DBController()


@router.get("/user-info")
async def get_user_info(user_id: str):
    user_info = await db_controller.select_user(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info


@router.get("/all-users")
async def get_all_user_info(limit: int = 10):
    user_info = await db_controller.select_users(limit)
    return user_info

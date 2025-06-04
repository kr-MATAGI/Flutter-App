from fastapi import APIRouter, HTTPException

from app.routers.controller.db_ctl import DBController

router = APIRouter()
db_controller = DBController()


@router.get("/menu-all")
async def get_menu_info(store_name: str):
    try:
        result = await db_controller.select_menu_info(store_name)
        return {
            "status": "success",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

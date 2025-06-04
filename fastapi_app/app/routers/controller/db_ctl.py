from sqlalchemy import text

from app.core.database import get_db
from app.utils.logger import setup_logger
from app.models.menu_base import MenuInfo

logger = setup_logger("DB_Controller")


class DBController:
    def __init__(self):
        logger.info("DBController initialized")

    ### 사용자 정보 관련
    async def select_user(self, user_id: str):
        """사용자 ID로 단일 사용자 정보를 조회합니다."""
        db = get_db()
        async for session in db:
            result = await session.execute(
                text(
                    """
                    SELECT * FROM user_info 
                    WHERE user_id = :user_id
                    """
                ),
                {"user_id": user_id},
            )
            return [dict(row) for row in result.mappings()]

    async def select_users(self, limit: int = 10):
        """전체 사용자 목록을 조회합니다."""
        db = get_db()
        async for session in db:
            result = await session.execute(
                text(
                    """
                    SELECT * FROM user_info 
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            )
            return [dict(row) for row in result.mappings()]

    ### 메뉴 정보 관련
    async def insert_menu_info(self, menu_info: MenuInfo):
        """메뉴 정보를 삽입합니다."""
        db = get_db()
        async for session in db:
            try:
                await session.execute(
                    text(
                        """
                        INSERT INTO menu_info (
                            user_id, store_name, file_name, menu_name, cost
                        ) VALUES (
                            :user_id, :store_name, :file_name, :menu_name, :cost
                        )"""
                    ),
                    {
                        "user_id": menu_info.user_id,
                        "store_name": menu_info.store_name,
                        "file_name": menu_info.file_name,
                        "menu_name": menu_info.menu_name,
                        "cost": menu_info.cost,
                    },
                )
                await session.commit()
            except Exception as e:
                logger.error(f"메뉴 정보 삽입 중 오류 발생: {str(e)}")

    async def select_menu_info(self, store_name: str):
        """특정 가게의 메뉴 정보를 조회합니다."""
        db = get_db()
        async for session in db:
            try:
                result = await session.execute(
                    text(
                        """
                        SELECT menu_name, cost FROM menu_info
                        WHERE store_name = :store_name
                    """
                    ),
                    {"store_name": store_name},
                )
                return [dict(row) for row in result.mappings()]
            except Exception as e:
                logger.error(f"{store_name} 메뉴 정보 조회 중 오류 발생: {str(e)}")

    # @TODO
    async def select_best_menu(self, store_name: str, top_k: int = 5):
        """특정 가게에서 가장 잘 팔리는 메뉴를 조회 합니다."""
        db = get_db()
        async for session in db:
            try:
                result = await session.execute(
                    text(
                        """
                        """
                    ),
                    {},
                )
            except Exception as e:
                logger.error(
                    f"{store_name} 가장 잘 팔리는 메뉴 조회 중 오류 발생: {str(e)}"
                )

    ### 주문 정보 관련
    async def select_user_order_history(self, user_id: str, limit_days: int = 7):
        """
        사용자의 주문 내역을 조회합니다. (최대 7일)
        """
        pass

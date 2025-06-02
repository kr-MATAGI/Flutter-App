from sqlalchemy import text

from app.core.database import get_db
from app.utils.logger import setup_logger

logger = setup_logger("DB_Controller")


class DBController:
    def __init__(self):
        logger.info("DBController initialized")

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

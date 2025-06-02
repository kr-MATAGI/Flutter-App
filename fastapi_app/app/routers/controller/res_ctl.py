import psutil
from typing import Dict, Optional
from datetime import datetime

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("mcp_ctl")


class ResController:
    """Resource Controller for Memory Monitoring"""

    _instance: Optional["ResController"] = None

    def __new__(cls) -> "ResController":
        if cls._instance is None:
            cls._instance = super(ResController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.process = psutil.Process()
            logger.info("MCP Controller initialized")

    async def get_memory_usage(self) -> Dict:
        """현재 서버의 메모리 사용량을 반환합니다."""
        try:
            # 프로세스 메모리 정보
            process_memory = self.process.memory_info()

            # 시스템 메모리 정보
            system_memory = psutil.virtual_memory()

            memory_info = {
                "timestamp": datetime.now().isoformat(),
                "process": {
                    "rss": process_memory.rss / 1024 / 1024,  # MB
                    "vms": process_memory.vms / 1024 / 1024,  # MB
                    "percent": self.process.memory_percent(),
                },
                "system": {
                    "total": system_memory.total / 1024 / 1024,  # MB
                    "available": system_memory.available / 1024 / 1024,  # MB
                    "used": system_memory.used / 1024 / 1024,  # MB
                    "percent": system_memory.percent,
                },
            }

            logger.info(f"Memory usage collected: {memory_info}")
            return memory_info

        except Exception as e:
            logger.error(f"Error getting memory usage: {str(e)}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def get_memory_alert(self) -> Dict:
        """메모리 사용량이 임계치를 넘었는지 확인합니다."""
        try:
            memory_info = await self.get_memory_usage()

            # 임계치 설정 (예: 시스템 메모리 80%, 프로세스 메모리 50%)
            system_threshold = settings.SYSTEM_MEM_THRESHOLD
            process_threshold = settings.PROCESS_MEM_THRESHOLD

            alerts = []
            if memory_info["system"]["percent"] > system_threshold:
                alerts.append(
                    f"시스템 메모리 사용량이 {system_threshold}%를 초과했습니다."
                )

            if memory_info["process"]["percent"] > process_threshold:
                alerts.append(
                    f"프로세스 메모리 사용량이 {process_threshold}%를 초과했습니다."
                )

            return {
                "has_alert": len(alerts) > 0,
                "alerts": alerts,
                "memory_info": memory_info,
            }

        except Exception as e:
            logger.error(f"Error checking memory alerts: {str(e)}")
            return {
                "has_alert": True,
                "alerts": [f"메모리 모니터링 중 오류 발생: {str(e)}"],
                "error": str(e),
            }

    def __str__(self) -> str:
        return "Model Context Protocol Controller (Memory Monitor)"

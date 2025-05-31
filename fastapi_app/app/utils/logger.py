import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "fastapi_app") -> logging.Logger:
    """
    애플리케이션에서 사용할 로거를 설정하고 반환합니다.

    Args:
        name (str): 로거의 이름 (기본값: "fastapi_app")

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    # 로거 인스턴스 생성
    logger = logging.getLogger(name)

    # 로그 레벨 설정 (DEBUG 레벨부터 모든 로그를 캡처)
    logger.setLevel(logging.DEBUG)

    # 이미 핸들러가 설정되어 있다면 추가 설정하지 않음
    if logger.handlers:
        return logger

    # 로그 포맷 설정
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # 파일 핸들러 설정
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


# 기본 로거 인스턴스 생성
logger = setup_logger()

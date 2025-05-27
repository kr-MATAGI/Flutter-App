import logging
import logging.handlers
import os
from datetime import datetime


def setup_logger(
    name: str = "kafka_logger", log_level: int = logging.INFO
) -> logging.Logger:
    """
    로깅을 설정하고 로거 인스턴스를 반환합니다.

    Args:
        name (str): 로거의 이름
        log_level (int): 로깅 레벨 (기본값: logging.INFO)

    Returns:
        logging.Logger: 설정된 로거 인스턴스
    """
    # 로그 디렉토리 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 로거 인스턴스 생성
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 이미 핸들러가 설정되어 있다면 추가하지 않음
    if logger.handlers:
        return logger

    # 로그 포맷 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 파일 핸들러 설정 (일별 로그 파일 생성)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, f"{name}.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 기본 로거 인스턴스 생성
logger = setup_logger()


def get_logger(
    name: str = "kafka_logger", log_level: int = logging.INFO
) -> logging.Logger:
    """
    로거 인스턴스를 반환합니다.

    Args:
        name (str): 로거의 이름
        log_level (int): 로깅 레벨

    Returns:
        logging.Logger: 로거 인스턴스
    """
    return setup_logger(name, log_level)


# 사용 예시
if __name__ == "__main__":
    test_logger = get_logger("test_logger")
    test_logger.info("Info 레벨 로그 메시지")
    test_logger.warning("Warning 레벨 로그 메시지")
    test_logger.error("Error 레벨 로그 메시지")
    test_logger.debug("Debug 레벨 로그 메시지")

import sys

from loguru import logger
from src.a_domain.ports.notification.logging_port import ILoggingPort


class LoguruAdapter(ILoggingPort):
    def __init__(self, level: str | int = "INFO"):
        logger.remove()
        logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
        )
        self._logger = logger

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def critical(self, message: str) -> None:
        self._logger.critical(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

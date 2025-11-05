from typing import Protocol


class ILoggingPort(Protocol):
    """
    Abstract interface for a logging service.
    """

    def info(self, message: str):
        """
        Log an info-level message with optional structured context.

        :param message: The message to log.
        :param kwargs: Additional key-value context for structured logging.
        """
        ...

    def warning(self, message: str):
        """
        Log a warning-level message with optional structured context.

        :param message: The message to log.
        :param kwargs: Additional key-value context for structured logging.
        """
        ...

    def debug(self, message: str):
        """
        Log a debug-level message with optional structured context.

        :param message: The message to log.
        :param kwargs: Additional key-value context for structured logging.
        """
        ...

    def critical(self, message: str):
        """
        Log a critical-level message with optional structured context.

        :param message: The message to log.
        :param kwargs: Additional key-value context for structured logging.
        """
        ...

    def error(self, message: str):
        """
        Log an error-level message with optional structured context.

        :param message: The message to log.
        :param kwargs: Additional key-value context for structured logging.
        """
        ...

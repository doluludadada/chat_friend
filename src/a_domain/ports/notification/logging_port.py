from typing import Protocol


class ILoggingPort(Protocol):
    """
    Abstract interface for a logging service.
    """

    def info(self, message: str):
        """
        Log an info-level message with optional structured context.

        :param message: The message to log.
        """
        ...

    def warning(self, message: str):
        """
        Log a warning-level message with optional structured context.

        :param message: The message to log.
        """
        ...

    def debug(self, message: str):
        """
        Log a debug-level message with optional structured context.

        :param message: The message to log.
        """
        ...

    def critical(self, message: str):
        """
        Log a critical-level message with optional structured context.

        :param message: The message to log.
        """
        ...

    def error(self, message: str):
        """
        Log an error-level message with optional structured context.

        :param message: The message to log.
        """
        ...

    def success(self, message: str):
        """Logs a message indicating a successful operation."""
        ...

    def trace(self, message: str):
        """Logs a message for fine-grained tracing, lower than DEBUG."""
        ...

    def exception(self, message: str):
        """
        Log an exception message, including a stack trace, with optional structured context.
        """
        ...

import base64
import hashlib
import hmac

from src.a_domain.ports.notification.logging_port import ILoggingPort


class LineSecurityService:
    """Handles LINE webhook signature validation."""

    def __init__(self, channel_secret: str, logger: ILoggingPort):
        if not channel_secret:
            raise ValueError("LINE channel secret is required for security validation.")
        self._channel_secret_bytes = channel_secret.encode("utf-8")
        self._logger = logger

    def verify_signature(self, request_body: bytes, signature: str | None) -> bool:
        if not signature:
            self._logger.warning("No X-Line-Signature found in request headers.")
            return False

        try:
            my_hash = hmac.new(self._channel_secret_bytes, request_body, hashlib.sha256).digest()
            expected_signature = base64.b64encode(my_hash).decode("utf-8")
            if hmac.compare_digest(signature, expected_signature):
                self._logger.trace("LINE signature validation successful.")
                return True
            else:
                self._logger.warning(f"Invalid signature. Expected: {expected_signature}, Got: {signature}")
                return False
        except Exception as e:
            self._logger.error(f"An exception occurred during signature validation: {e}")
            return False

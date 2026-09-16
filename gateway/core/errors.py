from __future__ import annotations

from dataclasses import dataclass


class GatewayError(Exception):
    """Base error with a normalized error code and HTTP status."""

    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self, request_id: str = "") -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "request_id": request_id,
            }
        }


# --- Gateway error codes ---

class InvalidRequestError(GatewayError):
    def __init__(self, message: str = "Invalid request."):
        super().__init__("INVALID_REQUEST", message, 400)


class UnauthorizedError(GatewayError):
    def __init__(self, message: str = "Unauthorized."):
        super().__init__("UNAUTHORIZED", message, 401)


class ModelNotAllowedError(GatewayError):
    def __init__(self, message: str = "Model not allowed."):
        super().__init__("MODEL_NOT_ALLOWED", message, 403)


class PolicyViolationError(GatewayError):
    def __init__(self, message: str = "Policy violation."):
        super().__init__("POLICY_VIOLATION", message, 403)


class RateLimitExceededError(GatewayError):
    def __init__(self, message: str = "Rate limit exceeded."):
        super().__init__("RATE_LIMIT_EXCEEDED", message, 429)


class QuotaExceededError(GatewayError):
    def __init__(self, message: str = "Quota exceeded."):
        super().__init__("QUOTA_EXCEEDED", message, 429)


# --- Provider errors ---

class ProviderRateLimitedError(GatewayError):
    def __init__(self, message: str = "Upstream provider is rate limiting."):
        super().__init__("PROVIDER_RATE_LIMITED", message, 502)


class ProviderTimeoutError(GatewayError):
    def __init__(self, message: str = "Upstream provider timed out."):
        super().__init__("PROVIDER_TIMEOUT", message, 504)


class ProviderUnavailableError(GatewayError):
    def __init__(self, message: str = "Upstream provider unavailable."):
        super().__init__("PROVIDER_UNAVAILABLE", message, 502)


class ProviderError(GatewayError):
    def __init__(self, message: str = "Upstream provider error."):
        super().__init__("PROVIDER_ERROR", message, 502)


class InternalError(GatewayError):
    def __init__(self, message: str = "Internal error."):
        super().__init__("INTERNAL_ERROR", message, 500)


# --- Error code registry ---

ERROR_CODES: dict[str, type[GatewayError]] = {
    "INVALID_REQUEST": InvalidRequestError,
    "UNAUTHORIZED": UnauthorizedError,
    "MODEL_NOT_ALLOWED": ModelNotAllowedError,
    "POLICY_VIOLATION": PolicyViolationError,
    "RATE_LIMIT_EXCEEDED": RateLimitExceededError,
    "QUOTA_EXCEEDED": QuotaExceededError,
    "PROVIDER_RATE_LIMITED": ProviderRateLimitedError,
    "PROVIDER_TIMEOUT": ProviderTimeoutError,
    "PROVIDER_UNAVAILABLE": ProviderUnavailableError,
    "PROVIDER_ERROR": ProviderError,
    "INTERNAL_ERROR": InternalError,
}

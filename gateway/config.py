from __future__ import annotations

from pydantic_settings import BaseSettings

# In-memory runtime overrides (volatile — lost on restart)
# These take precedence over env-based settings
_runtime_overrides: dict[str, str] = {}


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # Provider credentials (fallback — runtime overrides win)
    openai_api_key: str = ""
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    groq_api_key:str = ""

    # Default provider selection
    default_provider: str = "openai"

    # Request defaults
    default_model: str = "gpt-4o-mini"
    default_max_tokens: int = 4096
    default_temperature: float = 0.7

    # Provider timeouts (seconds)
    provider_timeout: float = 30.0

    # API config
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # API key hash secret (Phase 4+)
    api_key_hash_secret: str = ""


settings = Settings()


def get_api_key(name: str) -> str:
    """Return runtime override if set, otherwise env-based value."""
    if name in _runtime_overrides:
        return _runtime_overrides[name]
    return getattr(settings, name, "")


def set_api_key(name: str, value: str) -> None:
    """Set a runtime override for a provider API key."""
    _runtime_overrides[name] = value


def mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return key[:4] + "****"
    return key[:6] + "****" + key[-4:]

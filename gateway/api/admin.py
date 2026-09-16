from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from gateway.config import get_api_key, mask_key, set_api_key, settings

router = APIRouter(prefix="/admin")


class SettingsUpdate(BaseModel):
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None


@router.get("/settings")
async def get_settings():
    """Return current provider key status (masked)."""
    return {
        "openai_api_key": mask_key(get_api_key("openai_api_key")),
        "openrouter_api_key": mask_key(get_api_key("openrouter_api_key")),
        "has_openai_env": bool(settings.openai_api_key),
        "has_openrouter_env": bool(settings.openrouter_api_key),
    }


@router.put("/settings")
async def update_settings(body: SettingsUpdate):
    """Update provider API keys at runtime."""
    if body.openai_api_key is not None:
        set_api_key("openai_api_key", body.openai_api_key)
    if body.openrouter_api_key is not None:
        set_api_key("openrouter_api_key", body.openrouter_api_key)
    return {"status": "updated"}

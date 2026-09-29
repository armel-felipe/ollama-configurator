from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.ollama.client import get_ollama_client
from backend.ollama.runtime import RuntimeProfileService
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore

router = APIRouter(prefix="/api")


class RuntimeStatusResponse(BaseModel):
    model: str
    loaded: bool
    context: int | None = None
    requested_context: int | None = None
    context_matches: bool | None = None
    processor: str | None = None
    until: str | None = None
    applied_options: dict[str, Any] = Field(default_factory=dict)
    observed_at: str


def get_runtime_service() -> RuntimeProfileService:
    return RuntimeProfileService(ConfigStore(user_data_dir() / "config.json"), get_ollama_client())


@router.get("/models/{model_id}/runtime", response_model=RuntimeStatusResponse)
def model_runtime(model_id: str) -> RuntimeStatusResponse:
    return RuntimeStatusResponse(**get_runtime_service().status(model_id))

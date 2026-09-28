from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.ollama.client import OllamaError, get_ollama_client
from backend.ollama.options import ModelSettingsService, extract_model_defaults, validate_thinking
from backend.ollama.runtime import RuntimeProfileService
from backend.ollama.schemas import ThinkingSpec
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore

router = APIRouter(prefix="/api")


class ModelSettingsResponse(BaseModel):
    model: str
    options: dict[str, Any] = Field(default_factory=dict)
    thinking: ThinkingSpec | None = None
    defaults: dict[str, str] = Field(default_factory=dict)


class ApplyModelSettingsResponse(BaseModel):
    model: str
    applied: bool
    runtime: dict[str, Any] | None = None


def get_model_settings_service() -> ModelSettingsService:
    return ModelSettingsService(
        store=ConfigStore(user_data_dir() / "config.json"),
        client=get_ollama_client(),
    )


@router.get("/models/{model_id}/settings", response_model=ModelSettingsResponse)
def get_model_settings(model_id: str) -> ModelSettingsResponse:
    service = get_model_settings_service()
    model_spec = service.client.show_model(model_id)
    spec = model_spec.get("thinking")
    thinking = ThinkingSpec.model_validate(spec) if isinstance(spec, dict) else None
    defaults = extract_model_defaults(model_spec)
    if thinking and thinking.default is not None:
        defaults["think"] = str(thinking.default)
    return ModelSettingsResponse(
        model=model_id,
        options=service.get(model_id),
        thinking=thinking,
        defaults=defaults,
    )


@router.put("/models/{model_id}/settings", response_model=ModelSettingsResponse)
def update_model_settings(model_id: str, patch: dict[str, Any]) -> ModelSettingsResponse:
    try:
        service = get_model_settings_service()
        if "think" in patch and patch["think"] != "default":
            spec = service.client.show_model(model_id).get("thinking", {})
            validate_thinking(patch["think"], spec)
        options = service.update(model_id, patch)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ModelSettingsResponse(model=model_id, options=options)


@router.delete("/models/{model_id}/settings/{parameter}", response_model=ModelSettingsResponse)
def reset_model_parameter(model_id: str, parameter: str) -> ModelSettingsResponse:
    try:
        options = get_model_settings_service().reset_parameter(model_id, parameter)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ModelSettingsResponse(model=model_id, options=options)


@router.post("/models/{model_id}/apply", response_model=ApplyModelSettingsResponse)
def apply_model_settings(model_id: str) -> ApplyModelSettingsResponse:
    try:
        service = get_model_settings_service()
        service.apply(model_id)
        runtime = RuntimeProfileService(service.store, service.client).status(model_id)
    except (OllamaError, ValueError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return ApplyModelSettingsResponse(model=model_id, applied=True, runtime=runtime)

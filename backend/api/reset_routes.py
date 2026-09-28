from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.ollama.options import SUPPORTED_OPTIONS
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore

router = APIRouter(prefix="/api")


class ResetResult(BaseModel):
    reset: bool
    model: str | None = None
    removed_options: dict[str, Any] = Field(default_factory=dict)


class ResetService:
    def __init__(self, store: ConfigStore) -> None:
        self.store = store

    def reset_all_models(self) -> ResetResult:
        config = self.store.load()
        removed = dict(config.get("models", {}))
        config["models"] = {}
        self.store.save(config)
        return ResetResult(reset=True, removed_options=removed)

    def reset_model(self, model_id: str) -> ResetResult:
        config = self.store.load()
        removed = dict(config.get("models", {}).pop(model_id, {}))
        self.store.save(config)
        return ResetResult(reset=True, model=model_id, removed_options=removed)

    def reset_parameter(self, model_id: str, parameter: str) -> ResetResult:
        if parameter not in SUPPORTED_OPTIONS:
            raise ValueError(f"unsupported model option: {parameter}")
        config = self.store.load()
        models = config.setdefault("models", {})
        current = dict(models.get(model_id, {}))
        removed = {parameter: current.pop(parameter)} if parameter in current else {}
        if current:
            models[model_id] = current
        else:
            models.pop(model_id, None)
        self.store.save(config)
        return ResetResult(reset=True, model=model_id, removed_options=removed)


def get_reset_service() -> ResetService:
    return ResetService(ConfigStore(user_data_dir() / "config.json"))


@router.post("/reset/models", response_model=ResetResult)
def reset_all_models() -> ResetResult:
    return get_reset_service().reset_all_models()


@router.post("/models/{model_id}/reset", response_model=ResetResult)
def reset_model(model_id: str) -> ResetResult:
    return get_reset_service().reset_model(model_id)


@router.post("/models/{model_id}/settings/{parameter}/reset", response_model=ResetResult)
def reset_model_parameter(model_id: str, parameter: str) -> ResetResult:
    try:
        return get_reset_service().reset_parameter(model_id, parameter)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

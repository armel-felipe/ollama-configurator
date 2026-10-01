import platform
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.ollama.client import get_ollama_client
from backend.ollama.options import ModelSettingsService
from backend.os_adapters.macos import MacOSAdapter
from backend.os_adapters.windows import WindowsAdapter
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore
from backend.server_settings.restart_coordinator import RestartCoordinator
from backend.server_settings.service import ServerSettingsService, ServerSettingsState

router = APIRouter(prefix="/api")


class ServerSettingsResponse(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)
    effective: dict[str, Any] = Field(default_factory=dict)
    pending_restart: bool
    available: bool
    capabilities: dict[str, dict[str, Any]] = Field(default_factory=dict)


class RestartResponse(BaseModel):
    success: bool
    detail: str
    reapplied_models: list[str] = Field(default_factory=list)


def get_server_settings_service() -> ServerSettingsService:
    adapter = MacOSAdapter() if platform.system() == "Darwin" else WindowsAdapter()
    return ServerSettingsService(user_data_dir() / "config.json", adapter)


def get_restart_coordinator() -> RestartCoordinator:
    service = get_server_settings_service()
    model_service = ModelSettingsService(ConfigStore(service.store.path), get_ollama_client())
    return RestartCoordinator(service.store.path, service.adapter, model_service)


def _response(state: ServerSettingsState) -> ServerSettingsResponse:
    return ServerSettingsResponse(
        settings=state.settings,
        effective=state.effective,
        pending_restart=state.pending_restart,
        available=state.available,
        capabilities=state.capabilities,
    )


@router.get("/server/settings", response_model=ServerSettingsResponse)
def get_server_settings() -> ServerSettingsResponse:
    try:
        return _response(get_server_settings_service().get())
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/server/runtime", response_model=ServerSettingsResponse)
def get_server_runtime() -> ServerSettingsResponse:
    return get_server_settings()


@router.put("/server/settings", response_model=ServerSettingsResponse)
def update_server_settings(patch: dict[str, Any]) -> ServerSettingsResponse:
    try:
        return _response(get_server_settings_service().update(patch))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (OSError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/server/settings/reset", response_model=ServerSettingsResponse)
def reset_server_settings() -> ServerSettingsResponse:
    try:
        return _response(get_server_settings_service().reset())
    except (OSError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/server/restart", response_model=RestartResponse)
def restart_server() -> RestartResponse:
    try:
        result = get_restart_coordinator().restart_and_reapply_profiles()
    except (OSError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return RestartResponse(
        success=result.success,
        detail=result.detail,
        reapplied_models=result.reapplied_models,
    )

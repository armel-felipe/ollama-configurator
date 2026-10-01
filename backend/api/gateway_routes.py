from fastapi import APIRouter, HTTPException

from backend.gateway_manager import GatewayManagerError, GatewayProcessManager, GatewayStatus
from backend.gateway_settings import DEFAULT_GATEWAY_HOST, GatewaySettingsService
from backend.persistence.paths import user_data_dir
from backend.persistence.store import ConfigStore

router = APIRouter(prefix="/api/gateway")


def configured_gateway_host() -> str:
    try:
        return GatewaySettingsService(
            ConfigStore(user_data_dir() / "config.json")
        ).get(effective_host=DEFAULT_GATEWAY_HOST).host
    except (OSError, ValueError):
        return DEFAULT_GATEWAY_HOST


_manager = GatewayProcessManager(host=configured_gateway_host())


def get_gateway_manager() -> GatewayProcessManager:
    return _manager


def _result(status: GatewayStatus) -> dict[str, object]:
    return status.to_dict()


@router.get("/status")
def gateway_status() -> dict[str, object]:
    return _result(get_gateway_manager().status())


@router.post("/start")
def gateway_start() -> dict[str, object]:
    try:
        return _result(get_gateway_manager().start())
    except GatewayManagerError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/stop")
def gateway_stop() -> dict[str, object]:
    try:
        return _result(get_gateway_manager().stop())
    except GatewayManagerError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/restart")
def gateway_restart() -> dict[str, object]:
    try:
        return _result(get_gateway_manager().restart())
    except GatewayManagerError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/release-external")
def gateway_release_external() -> dict[str, object]:
    try:
        return _result(get_gateway_manager().release_external())
    except GatewayManagerError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

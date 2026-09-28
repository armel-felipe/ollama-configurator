from fastapi import APIRouter, HTTPException

from backend.gateway_manager import GatewayManagerError, GatewayProcessManager, GatewayStatus

router = APIRouter(prefix="/api/gateway")
_manager = GatewayProcessManager()


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

from fastapi import APIRouter, HTTPException

from backend.app_lifecycle import request_restart

router = APIRouter(prefix="/api/application")


@router.post("/restart")
def restart_application() -> dict[str, str]:
    try:
        request_restart()
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"status": "restarting"}

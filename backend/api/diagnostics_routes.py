from fastapi import APIRouter

from backend.diagnostics.service import DiagnosticsSnapshot, collect_diagnostics
from backend.hardware.detector import HardwareDetector, get_hardware_detector
from backend.ollama.client import get_ollama_client

router = APIRouter(prefix="/api")


@router.get("/hardware")
def hardware() -> object:
    return get_hardware_detector().detect()


@router.get("/diagnostics", response_model=DiagnosticsSnapshot)
def diagnostics() -> DiagnosticsSnapshot:
    detector: HardwareDetector = get_hardware_detector()
    return collect_diagnostics(get_ollama_client(), detector)

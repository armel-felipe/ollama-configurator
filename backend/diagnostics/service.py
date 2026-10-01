from pydantic import BaseModel

from backend.hardware.detector import HardwareDetector
from backend.hardware.schemas import HardwareSnapshot
from backend.ollama.client import OllamaClient
from backend.ollama.discovery import discover_ollama
from backend.ollama.schemas import OllamaModel, OllamaStatusResponse
from backend.version import get_version


class DiagnosticsSnapshot(BaseModel):
    application_version: str
    ollama: OllamaStatusResponse
    hardware: HardwareSnapshot
    models: list[OllamaModel]


def collect_diagnostics(client: OllamaClient, detector: HardwareDetector) -> DiagnosticsSnapshot:
    ollama = discover_ollama(client)
    models: list[OllamaModel] = []
    if ollama.available:
        try:
            models = client.list_models()
        except Exception:
            models = []
    return DiagnosticsSnapshot(application_version=get_version(), ollama=ollama, hardware=detector.detect(), models=models)

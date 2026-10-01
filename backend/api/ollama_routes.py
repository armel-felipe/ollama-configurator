from fastapi import APIRouter

from backend.ollama.capabilities import available_capabilities
from backend.ollama.client import OllamaClient, get_ollama_client
from backend.ollama.discovery import discover_ollama
from backend.ollama.schemas import CapabilitiesResponse, ModelsResponse, OllamaStatusResponse

router = APIRouter(prefix="/api")


@router.get("/ollama/status", response_model=OllamaStatusResponse)
def ollama_status() -> OllamaStatusResponse:
    return discover_ollama(get_ollama_client())


@router.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    client: OllamaClient = get_ollama_client()
    return ModelsResponse(models=client.list_models())


@router.get("/capabilities", response_model=CapabilitiesResponse)
def capabilities() -> CapabilitiesResponse:
    return available_capabilities()

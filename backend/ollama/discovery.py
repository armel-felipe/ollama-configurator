from backend.ollama.client import OllamaClient
from backend.ollama.schemas import OllamaStatusResponse


def discover_ollama(client: OllamaClient) -> OllamaStatusResponse:
    try:
        return OllamaStatusResponse(available=True, version=client.get_version().version)
    except Exception as error:
        return OllamaStatusResponse(available=False, error=str(error))

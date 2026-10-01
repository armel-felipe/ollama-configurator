import httpx
import pytest

from backend.ollama.client import OllamaClient, OllamaConnectionError


def test_client_reads_version_and_models_from_ollama() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "0.5.7"})
        return httpx.Response(200, json={"models": [{"name": "qwen:latest", "size": 123}]})

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))

    assert client.get_version().version == "0.5.7"
    assert client.list_models()[0].name == "qwen:latest"


def test_client_normalizes_connection_failure() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline")

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))

    with pytest.raises(OllamaConnectionError, match="unavailable"):
        client.get_version()

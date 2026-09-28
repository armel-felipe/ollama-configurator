import httpx
import pytest

from backend.app import app
from backend.ollama.client import OllamaClient


@pytest.mark.asyncio
async def test_status_and_models_routes_expose_discovery_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OllamaClient(
        "http://ollama",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"version": "0.5.7"}
                if request.url.path == "/api/version"
                else {"models": [{"name": "qwen:latest", "size": 123}]},
            )
        ),
    )
    monkeypatch.setattr("backend.api.ollama_routes.get_ollama_client", lambda: client)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        status = await http_client.get("/api/ollama/status")
        models = await http_client.get("/api/models")

    assert status.status_code == 200
    assert status.json()["version"] == "0.5.7"
    assert models.json()["models"][0]["name"] == "qwen:latest"

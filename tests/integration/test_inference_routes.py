from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.ollama.client import OllamaClient
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_inference_route_returns_profile_response_and_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"gemma4:26b-mlx": {"num_ctx": 16384, "think": False}}, "server": {}})

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/generate":
            payload = request.read()
            assert b'"think":false' in payload
            return httpx.Response(200, json={"response": "Jânio Quadros", "done": True})
        if request.url.path == "/api/ps":
            return httpx.Response(
                200,
                json={"models": [{"name": "gemma4:26b-mlx", "context_length": 16384}]},
            )
        raise AssertionError(request.url.path)

    from backend.inference.service import InferenceService

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))
    monkeypatch.setattr(
        "backend.api.inference_routes.get_inference_service",
        lambda: InferenceService(store, client),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        response = await http_client.post(
            "/api/models/gemma4:26b-mlx/inference-test",
            json={"prompt": "Quem foi o 23º presidente do Brasil?"},
        )

    assert response.status_code == 200
    assert response.json()["response"] == "Jânio Quadros"
    assert response.json()["thinking_received"] is False
    assert response.json()["runtime"]["context"] == 16384


@pytest.mark.asyncio
async def test_inference_route_rejects_blank_prompt() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        response = await http_client.post(
            "/api/models/qwen:latest/inference-test", json={"prompt": " "}
        )

    assert response.status_code == 422

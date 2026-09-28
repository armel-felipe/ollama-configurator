from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.ollama.client import OllamaClient
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_settings_expose_model_thinking_and_runtime_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = ConfigStore(tmp_path / "config.json")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/show":
            return httpx.Response(
                200, json={"thinking": {"values": [False, "low", "high"], "default": "low"}}
            )
        if request.url.path == "/api/ps":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {"name": "qwen:latest", "context_length": 65536, "processor": "100% GPU"}
                    ]
                },
            )
        if request.url.path == "/api/generate":
            return httpx.Response(200, json={"response": "", "thinking": "trace", "done": True})
        raise AssertionError(request.url.path)

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))
    monkeypatch.setattr(
        "backend.api.model_settings_routes.get_model_settings_service",
        lambda: _service(store, client),
    )
    monkeypatch.setattr(
        "backend.api.model_runtime_routes.get_runtime_service",
        lambda: _runtime_service(store, client),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        update = await http_client.put(
            "/api/models/qwen:latest/settings", json={"num_ctx": 65536, "think": "high"}
        )
        read = await http_client.get("/api/models/qwen:latest/settings")
        applied = await http_client.post("/api/models/qwen:latest/apply")
        runtime = await http_client.get("/api/models/qwen:latest/runtime")

    assert update.status_code == 200
    assert read.json()["thinking"] == {"values": [False, "low", "high"], "default": "low"}
    assert applied.status_code == 200
    assert applied.json()["runtime"]["context"] == 65536
    assert runtime.json()["context"] == 65536
    assert runtime.json()["applied_options"] == {"num_ctx": 65536, "think": "high"}


def _service(store: ConfigStore, client: OllamaClient):
    from backend.ollama.options import ModelSettingsService

    return ModelSettingsService(store=store, client=client)


def _runtime_service(store: ConfigStore, client: OllamaClient):
    from backend.ollama.runtime import RuntimeProfileService

    return RuntimeProfileService(store=store, client=client)

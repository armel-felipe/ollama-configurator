import json
from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.ollama.client import OllamaClient
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_model_settings_round_trip_for_tagged_model(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = ConfigStore(tmp_path / "config.json")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/show":
            return httpx.Response(200, json={})
        if request.url.path == "/api/ps":
            return httpx.Response(200, json={"models": []})
        assert request.url.path == "/api/generate"
        payload = json.loads(request.content)
        assert payload["model"] == "qwen:latest"
        if payload.get("keep_alive") == 0:
            assert payload["options"] == {}
        else:
            assert payload["options"] == {"temperature": 0.2, "num_ctx": 32768}
        return httpx.Response(200, json={"response": "", "done": True})

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))
    monkeypatch.setattr(
        "backend.api.model_settings_routes.get_model_settings_service",
        lambda: _service(store, client),
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        update = await http_client.put(
            "/api/models/qwen:latest/settings",
            json={"temperature": 0.2, "num_ctx": 32768},
        )
        read = await http_client.get("/api/models/qwen:latest/settings")
        applied = await http_client.post("/api/models/qwen:latest/apply")
        reset = await http_client.delete("/api/models/qwen:latest/settings/temperature")

    assert update.status_code == 200
    assert read.json()["options"] == {"temperature": 0.2, "num_ctx": 32768}
    assert applied.status_code == 200
    assert reset.json()["options"] == {"num_ctx": 32768}


def _service(store: ConfigStore, client: OllamaClient):
    from backend.ollama.options import ModelSettingsService

    return ModelSettingsService(store=store, client=client)

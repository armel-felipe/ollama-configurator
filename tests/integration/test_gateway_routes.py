from pathlib import Path

import httpx
import pytest

from backend.gateway import create_gateway_app
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_gateway_supports_ollama_generate_and_requires_key(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"gemma4:26b-mlx": {"think": False}}, "server": {}})
    captured: dict[str, object] = {}

    class FakeClient:
        def generate(self, _model: str, **kwargs: object) -> dict[str, object]:
            captured.update(kwargs)
            return {"response": "ok", "done": True}

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **_: object
        ) -> dict[str, object]:
            return {}

        def list_models(self) -> list[object]:
            return []

        def get_version(self) -> object:
            return {"version": "test"}

        def show_model(self, _model: str) -> dict[str, object]:
            return {}

        def list_running_models(self) -> list[dict[str, object]]:
            return []

    app = create_gateway_app(store=store, client=FakeClient(), api_key="secret")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        denied = await http_client.post(
            "/api/generate", json={"model": "gemma4:26b-mlx", "prompt": "Oi"}
        )
        response = await http_client.post(
            "/api/generate",
            headers={"x-api-key": "secret"},
            json={"model": "gemma4:26b-mlx", "prompt": "Oi", "stream": False},
        )

    assert denied.status_code == 401
    assert response.status_code == 200
    assert response.json()["response"] == "ok"
    assert captured["think"] is False


@pytest.mark.asyncio
async def test_gateway_openai_route_returns_sse_stream(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {}, "server": {}})

    class FakeClient:
        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {}

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **_: object
        ) -> dict[str, object]:
            return {}

        def chat_stream(self, _model: str, _messages: list[dict[str, object]], **_: object):
            yield {"message": {"role": "assistant", "content": "Olá"}, "done": False}
            yield {"message": {"role": "assistant", "content": " mundo"}, "done": True}

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
        response = await http_client.post(
            "/v1/chat/completions",
            json={"model": "qwen:latest", "messages": [], "stream": True},
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert '"content": "Olá"' in response.text
    assert '"content": " mundo"' in response.text
    assert "data: [DONE]" in response.text

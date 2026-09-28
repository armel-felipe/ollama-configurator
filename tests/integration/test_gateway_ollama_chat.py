from pathlib import Path

import httpx
import pytest

from backend.gateway import create_gateway_app
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_native_ollama_chat_uses_saved_profile(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"gemma4:26b-mlx": {"num_ctx": 16384, "think": False}}, "server": {}})
    captured: dict[str, object] = {}

    class FakeClient:
        def chat(
            self, _model: str, _messages: list[dict[str, object]], **kwargs: object
        ) -> dict[str, object]:
            captured.update(kwargs)
            return {"message": {"role": "assistant", "content": "ok"}, "done": True}

        def chat_stream(self, _model: str, _messages: list[dict[str, object]], **_: object):
            yield {"message": {"role": "assistant", "content": "ok"}, "done": True}

        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {}

        def generate_stream(self, _model: str, **_: object):
            yield {}

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={
                "model": "gemma4:26b-mlx",
                "messages": [{"role": "user", "content": "Oi"}],
                "stream": False,
                "think": True,
                "options": {"num_ctx": 4096},
            },
        )

    assert response.status_code == 200
    assert response.json()["message"]["content"] == "ok"
    assert captured["think"] is False
    assert captured["options"] == {"num_ctx": 16384}


@pytest.mark.asyncio
async def test_gateway_healthcheck_supports_ollama_head_request(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {}, "server": {}})

    class FakeClient:
        pass

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.head("/")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_native_ollama_chat_stream_returns_ndjson(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"qwen:latest": {"think": False}}, "server": {}})

    class FakeClient:
        def chat(
            self, _model: str, _messages: list[dict[str, object]], **_: object
        ) -> dict[str, object]:
            return {}

        def chat_stream(self, _model: str, _messages: list[dict[str, object]], **kwargs: object):
            assert kwargs["think"] is False
            yield {"message": {"role": "assistant", "content": "Olá"}, "done": False}
            yield {"message": {"role": "assistant", "content": "!"}, "done": True}

        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {}

        def generate_stream(self, _model: str, **_: object):
            yield {}

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={"model": "qwen:latest", "messages": [], "stream": True},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert '"content": "Olá"' in response.text
    assert '"done": true' in response.text

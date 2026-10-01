from pathlib import Path

import httpx
import pytest

from backend.gateway import create_gateway_app
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_gateway_ollama_route_returns_ndjson_chunks(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"gemma4:26b-mlx": {"think": False}}, "server": {}})

    class FakeClient:
        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {}

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **_: object
        ) -> dict[str, object]:
            return {}

        def generate_stream(self, _model: str, **kwargs: object):
            assert kwargs["think"] is False
            yield {"response": "ok", "done": False}
            yield {"response": "", "done": True}

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/generate",
            json={"model": "gemma4:26b-mlx", "prompt": "Oi", "stream": True},
        )

    lines = response.text.strip().splitlines()
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    assert '"response": "ok"' in lines[0]
    assert '"done": true' in lines[-1]


@pytest.mark.asyncio
async def test_openai_streaming_error_uses_object_error_envelope(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"qwen3.8:27b-mlx": {"think": False}}, "server": {}})

    class FakeClient:
        def chat_stream(self, _model: str, _messages: list[dict[str, object]], **_: object):
            yield {"message": {"role": "assistant", "content": "Olá"}, "done": False}
            raise RuntimeError("Ollama chat stream failed")

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "qwen3.8:27b-mlx",
                "messages": [{"role": "user", "content": "oi"}],
                "stream": True,
            },
        )

    assert response.status_code == 200
    assert (
        '"error": {"message": "Ollama chat stream failed", "type": "server_error"}'
        in response.text
    )


@pytest.mark.asyncio
async def test_openai_streaming_normalizes_text_content_parts(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"qwen3.8:27b-mlx": {"think": False}}, "server": {}})
    captured: dict[str, object] = {}

    class FakeClient:
        def chat_stream(self, _model: str, messages: list[dict[str, object]], **_: object):
            captured["messages"] = messages
            yield {"message": {"role": "assistant", "content": "OK"}, "done": True}

    app = create_gateway_app(store=store, client=FakeClient())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/chat/completions",
            json={
                "model": "qwen3.8:27b-mlx",
                "messages": [{"role": "user", "content": [{"type": "text", "text": "oi"}]}],
                "stream": True,
            },
        )

    assert response.status_code == 200
    assert captured["messages"] == [{"role": "user", "content": "oi"}]

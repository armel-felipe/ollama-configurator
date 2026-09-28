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

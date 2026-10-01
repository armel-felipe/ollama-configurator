from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.app import _resolve_frontend_dir


def test_backend_finds_source_frontend_when_no_override_is_configured(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_CONFIGURATOR_FRONTEND_DIR", raising=False)

    frontend_dir = _resolve_frontend_dir()

    assert frontend_dir == Path(__file__).resolve().parents[2] / "frontend" / "dist"


@pytest.mark.asyncio
async def test_backend_root_serves_the_frontend_without_an_environment_override(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_CONFIGURATOR_FRONTEND_DIR", raising=False)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text

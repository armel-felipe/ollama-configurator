from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.persistence.store import ConfigStore


@pytest.mark.asyncio
async def test_global_and_model_reset_only_change_saved_overrides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save(
        {
            "models": {
                "qwen:latest": {"temperature": 0.2},
                "gemma:latest": {"num_ctx": 4096},
            },
            "server": {},
        }
    )
    monkeypatch.setattr("backend.api.reset_routes.get_reset_service", lambda: _service(store))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        one = await client.post("/api/models/qwen:latest/reset")
        remaining = store.load()
        all_models = await client.post("/api/reset/models")

    assert one.status_code == 200
    assert remaining["models"] == {"gemma:latest": {"num_ctx": 4096}}
    assert all_models.status_code == 200
    assert store.load()["models"] == {}


def _service(store: ConfigStore):
    from backend.api.reset_routes import ResetService

    return ResetService(store)

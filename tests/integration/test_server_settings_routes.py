import httpx
import pytest

from backend.app import app


class FakeService:
    def get(self):
        return type(
            "State",
            (),
            {
                "settings": {},
                "effective": {},
                "pending_restart": False,
                "available": True,
                "capabilities": {},
            },
        )()

    def update(self, patch):
        return type(
            "State",
            (),
            {
                "settings": patch,
                "effective": patch,
                "pending_restart": True,
                "available": True,
                "capabilities": {},
            },
        )()

    def reset(self):
        return self.get()


class FakeCoordinator:
    def restart_and_reapply_profiles(self):
        return type(
            "Result",
            (),
            {
                "success": True,
                "detail": "Ollama reiniciado e perfis reaplicados",
                "reapplied_models": ["gemma4:26b-mlx"],
            },
        )()


@pytest.mark.asyncio
async def test_server_settings_routes_expose_global_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "backend.api.server_settings_routes.get_server_settings_service", lambda: FakeService()
    )
    monkeypatch.setattr(
        "backend.api.server_settings_routes.get_restart_coordinator", lambda: FakeCoordinator()
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        read = await client.get("/api/server/settings")
        update = await client.put("/api/server/settings", json={"OLLAMA_KV_CACHE_TYPE": "q8_0"})
        restart = await client.post("/api/server/restart")

    assert read.status_code == 200
    assert update.json()["pending_restart"] is True
    assert restart.json()["success"] is True
    assert restart.json()["reapplied_models"] == ["gemma4:26b-mlx"]

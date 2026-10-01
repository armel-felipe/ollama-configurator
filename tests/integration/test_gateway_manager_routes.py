from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.gateway_settings import DEFAULT_GATEWAY_HOST
from backend.gateway_manager import GatewayStatus
from backend.persistence.store import ConfigStore


class FakeManager:
    def status(self) -> GatewayStatus:
        return GatewayStatus(state="stopped", host="127.0.0.1", port=11435)

    def start(self) -> GatewayStatus:
        return GatewayStatus(state="starting", host="127.0.0.1", port=11435, pid=99)

    def stop(self) -> GatewayStatus:
        return GatewayStatus(state="stopped", host="127.0.0.1", port=11435)

    def restart(self) -> GatewayStatus:
        return GatewayStatus(state="running", host="127.0.0.1", port=11435, pid=100)


def test_gateway_manager_host_is_loaded_from_persisted_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    ConfigStore(tmp_path / "config.json").save({
        "models": {},
        "server": {},
        "gateway": {"host": "0.0.0.0"},
    })
    monkeypatch.setattr("backend.api.gateway_routes.user_data_dir", lambda: tmp_path, raising=False)

    from backend.api.gateway_routes import configured_gateway_host

    assert configured_gateway_host() == "0.0.0.0"
    assert DEFAULT_GATEWAY_HOST == "127.0.0.1"


@pytest.mark.asyncio
async def test_gateway_lifecycle_routes_return_actionable_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("backend.api.gateway_routes.get_gateway_manager", lambda: FakeManager())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        status = await client.get("/api/gateway/status")
        started = await client.post("/api/gateway/start")
        stopped = await client.post("/api/gateway/stop")
        restarted = await client.post("/api/gateway/restart")

    assert status.json()["state"] == "stopped"
    assert started.json()["state"] == "starting"
    assert stopped.json()["state"] == "stopped"
    assert restarted.json()["state"] == "running"

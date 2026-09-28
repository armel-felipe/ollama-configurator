from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.gateway_manager import GatewayStatus


class FakeManager:
    def status(self) -> GatewayStatus:
        return GatewayStatus(state="stopped", host="127.0.0.1", port=11435)

    def start(self) -> GatewayStatus:
        return GatewayStatus(state="starting", host="127.0.0.1", port=11435, pid=99)

    def stop(self) -> GatewayStatus:
        return GatewayStatus(state="stopped", host="127.0.0.1", port=11435)

    def restart(self) -> GatewayStatus:
        return GatewayStatus(state="running", host="127.0.0.1", port=11435, pid=100)


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

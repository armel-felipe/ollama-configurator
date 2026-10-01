from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.gateway_manager import GatewayManagerError, GatewayStatus
from backend.persistence.store import ConfigStore


class FakeSettingsManager:
    host = "127.0.0.1"
    port = 11435

    def __init__(self, *, fail_on_restart: bool = False) -> None:
        self.restart_hosts: list[str | None] = []
        self.fail_on_restart = fail_on_restart

    def status(self) -> GatewayStatus:
        return GatewayStatus("running", self.host, self.port, pid=77)

    def restart(self, host: str | None = None) -> GatewayStatus:
        self.restart_hosts.append(host)
        if self.fail_on_restart:
            raise GatewayManagerError("Não foi possível abrir o bind da gateway")
        if host is not None:
            self.host = host
        return GatewayStatus("running", self.host, self.port, pid=77)


async def client_for(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    manager: FakeSettingsManager,
) -> httpx.AsyncClient:
    monkeypatch.setattr("backend.api.gateway_routes.get_gateway_manager", lambda: manager)
    monkeypatch.setattr("backend.api.gateway_routes.user_data_dir", lambda: tmp_path)
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_gateway_settings_default_and_update_are_explicitly_pending(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    manager = FakeSettingsManager()
    async with await client_for(monkeypatch, tmp_path, manager) as client:
        initial = await client.get("/api/gateway/settings")
        updated = await client.put("/api/gateway/settings", json={"host": "0.0.0.0"})

    assert initial.status_code == 200
    assert initial.json()["host"] == "127.0.0.1"
    assert initial.json()["pending_restart"] is False
    assert updated.status_code == 200
    assert updated.json()["host"] == "0.0.0.0"
    assert updated.json()["effective_host"] == "127.0.0.1"
    assert updated.json()["pending_restart"] is True
    assert ConfigStore(tmp_path / "config.json").load()["gateway"]["host"] == "0.0.0.0"


@pytest.mark.asyncio
async def test_gateway_settings_reject_invalid_host_with_422(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    async with await client_for(monkeypatch, tmp_path, FakeSettingsManager()) as client:
        response = await client.put("/api/gateway/settings", json={"host": "192.168.1.10"})

    assert response.status_code == 422
    assert "host" in response.json()["detail"]


@pytest.mark.asyncio
async def test_gateway_apply_restarts_only_gateway_with_saved_host(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    manager = FakeSettingsManager()
    ConfigStore(tmp_path / "config.json").save({
        "models": {},
        "server": {},
        "gateway": {"host": "0.0.0.0"},
    })

    async with await client_for(monkeypatch, tmp_path, manager) as client:
        response = await client.post("/api/gateway/apply")

    assert response.status_code == 200
    assert manager.restart_hosts == ["0.0.0.0"]
    assert response.json()["status"]["host"] == "0.0.0.0"
    assert response.json()["settings"]["effective_host"] == "0.0.0.0"
    assert response.json()["settings"]["pending_restart"] is False


@pytest.mark.asyncio
async def test_gateway_apply_preserves_actionable_bind_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    manager = FakeSettingsManager(fail_on_restart=True)
    ConfigStore(tmp_path / "config.json").save({
        "models": {},
        "server": {},
        "gateway": {"host": "0.0.0.0"},
    })

    async with await client_for(monkeypatch, tmp_path, manager) as client:
        response = await client.post("/api/gateway/apply")

    assert response.status_code == 409
    assert "bind" in response.json()["detail"]

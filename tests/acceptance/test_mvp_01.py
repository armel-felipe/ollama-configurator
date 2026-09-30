from pathlib import Path

import httpx
import pytest

from backend.app import app
from backend.hardware.detector import HardwareDetector
from backend.ollama.options import ModelSettingsService
from backend.ollama.schemas import OllamaModel, OllamaVersion
from backend.os_adapters.base import RestartResult
from backend.persistence.store import ConfigStore
from backend.server_settings.restart_coordinator import RestartCoordinator
from backend.server_settings.service import ServerSettingsService


class FakeOllama:
    def __init__(self) -> None:
        self.models = [OllamaModel(name="qwen:latest", size=123)]
        self.running: list[dict[str, object]] = []
        self.reloads: list[dict[str, object]] = []

    def get_version(self) -> OllamaVersion:
        return OllamaVersion(version="0.40.0-test")

    def list_models(self) -> list[OllamaModel]:
        return self.models

    def show_model(self, _model_id: str) -> dict[str, object]:
        return {
            "thinking": {"values": [False, True], "default": True},
            "model_info": {"fake.context_length": 131072},
        }

    def reload_model(
        self,
        model_id: str,
        options: dict[str, object],
        think: object = None,
        keep_alive: object = None,
    ) -> None:
        self.reloads.append(
            {"model": model_id, "options": options, "think": think, "keep_alive": keep_alive}
        )
        self.running = [
            {"name": model_id, "context_length": options.get("num_ctx"), "runner": "fake"}
        ]

    def list_running_models(self) -> list[dict[str, object]]:
        return list(self.running)


class FakeAdapter:
    def __init__(self) -> None:
        self.environment: dict[str, str] = {}
        self.restart_count = 0

    def get_environment(self, name: str) -> str | None:
        return self.environment.get(name)

    def set_environment(self, name: str, value: str) -> None:
        self.environment[name] = value

    def remove_environment(self, name: str) -> None:
        self.environment.pop(name, None)

    def restart_ollama(self) -> RestartResult:
        self.restart_count += 1
        return RestartResult(True, "Ollama reiniciado")

    def open_logs(self) -> None:
        return None


@pytest.mark.asyncio
async def test_mvp_flow_discovers_configures_restarts_and_resets_without_deleting_models(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_ollama = FakeOllama()
    adapter = FakeAdapter()
    store = ConfigStore(tmp_path / "config.json")
    model_service = ModelSettingsService(store, fake_ollama)  # type: ignore[arg-type]
    server_service = ServerSettingsService(store.path, adapter)
    coordinator = RestartCoordinator(store.path, adapter, model_service, sleep=lambda _: None)

    monkeypatch.setattr("backend.api.ollama_routes.get_ollama_client", lambda: fake_ollama)
    monkeypatch.setattr("backend.api.diagnostics_routes.get_ollama_client", lambda: fake_ollama)
    monkeypatch.setattr(
        "backend.api.diagnostics_routes.get_hardware_detector",
        lambda: HardwareDetector("Darwin", "arm64", 36 * 1024**3, "Apple"),
    )
    monkeypatch.setattr(
        "backend.api.model_settings_routes.get_model_settings_service", lambda: model_service
    )
    monkeypatch.setattr(
        "backend.api.server_settings_routes.get_server_settings_service", lambda: server_service
    )
    monkeypatch.setattr(
        "backend.api.server_settings_routes.get_restart_coordinator", lambda: coordinator
    )
    monkeypatch.setattr("backend.api.reset_routes.get_reset_service", lambda: _reset_service(store))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        discovery = await client.get("/api/ollama/status")
        models = await client.get("/api/models")
        diagnostics = await client.get("/api/diagnostics")
        saved_model = await client.put(
            "/api/models/qwen:latest/settings",
            json={"num_ctx": 32768, "think": False},
        )
        applied_model = await client.post("/api/models/qwen:latest/apply")
        saved_server = await client.put(
            "/api/server/settings",
            json={"OLLAMA_KV_CACHE_TYPE": "q8_0"},
        )
        restarted = await client.post("/api/server/restart")
        reset = await client.post("/api/models/qwen:latest/reset")

    assert discovery.json() == {"available": True, "version": "0.40.0-test", "error": None}
    assert models.json()["models"][0]["name"] == "qwen:latest"
    assert diagnostics.json()["hardware"]["os"] == "macos"
    assert saved_model.json()["options"] == {"num_ctx": 32768, "think": False}
    assert applied_model.json()["runtime"]["context_matches"] is True
    assert fake_ollama.reloads[-1]["think"] is False
    assert saved_server.json()["pending_restart"] is True
    assert restarted.json()["success"] is True
    assert restarted.json()["reapplied_models"] == ["qwen:latest"]
    assert adapter.restart_count == 1
    assert reset.json()["reset"] is True
    assert store.load()["models"] == {}
    assert fake_ollama.list_models()[0].name == "qwen:latest"


def _reset_service(store: ConfigStore):
    from backend.api.reset_routes import ResetService

    return ResetService(store)

from pathlib import Path

import pytest

from backend.server_settings.service import ServerSettingsService


class FakeAdapter:
    def __init__(self) -> None:
        self.environment: dict[str, str] = {}
        self.events: list[str] = []

    def get_environment(self, name: str) -> str | None:
        return self.environment.get(name)

    def set_environment(self, name: str, value: str) -> None:
        self.events.append(f"set:{name}={value}")
        self.environment[name] = value

    def remove_environment(self, name: str) -> None:
        self.events.append(f"remove:{name}")
        self.environment.pop(name, None)


def test_server_settings_update_persists_and_marks_restart_pending(tmp_path: Path) -> None:
    adapter = FakeAdapter()
    service = ServerSettingsService(tmp_path / "config.json", adapter)

    updated = service.update({"OLLAMA_KV_CACHE_TYPE": "q8_0", "OLLAMA_FLASH_ATTENTION": True})

    assert updated.settings["OLLAMA_KV_CACHE_TYPE"] == "q8_0"
    assert updated.settings["OLLAMA_FLASH_ATTENTION"] is True
    assert updated.pending_restart is True
    assert adapter.environment["OLLAMA_KV_CACHE_TYPE"] == "q8_0"
    assert adapter.environment["OLLAMA_FLASH_ATTENTION"] == "true"

    reloaded = ServerSettingsService(tmp_path / "config.json", adapter).get()
    assert reloaded.settings == updated.settings


def test_server_settings_rejects_unsupported_kv_cache_value(tmp_path: Path) -> None:
    service = ServerSettingsService(tmp_path / "config.json", FakeAdapter())

    with pytest.raises(ValueError, match="KV cache"):
        service.update({"OLLAMA_KV_CACHE_TYPE": "int8"})


def test_reset_removes_overrides_instead_of_writing_arbitrary_defaults(tmp_path: Path) -> None:
    adapter = FakeAdapter()
    service = ServerSettingsService(tmp_path / "config.json", adapter)
    service.update({"OLLAMA_KV_CACHE_TYPE": "q4_0", "OLLAMA_CONTEXT_LENGTH": 32768})

    reset = service.reset()

    assert reset.settings == {}
    assert reset.pending_restart is True
    assert adapter.environment == {}
    assert "remove:OLLAMA_KV_CACHE_TYPE" in adapter.events


def test_coordinator_restarts_server_before_reapplying_model_profiles(tmp_path: Path) -> None:
    from backend.os_adapters.base import RestartResult
    from backend.server_settings.restart_coordinator import RestartCoordinator

    adapter = FakeAdapter()
    adapter.events.append("restart")

    class FakeModelService:
        def apply(self, model_id: str) -> None:
            adapter.events.append(f"model:{model_id}")

    config_path = tmp_path / "config.json"
    config_path.write_text('{"models":{"gemma4:26b-mlx":{"num_ctx":16384}},"server":{}}')
    coordinator = RestartCoordinator(config_path, adapter, FakeModelService())
    adapter.restart_ollama = lambda: adapter.events.append("restart") or RestartResult(True, "ok")  # type: ignore[attr-defined]

    result = coordinator.restart_and_reapply_profiles()

    assert result.success is True
    assert adapter.events[-2:] == ["restart", "model:gemma4:26b-mlx"]


def test_coordinator_retries_profiles_until_ollama_is_ready(tmp_path: Path) -> None:
    from backend.ollama.client import OllamaConnectionError
    from backend.os_adapters.base import RestartResult
    from backend.server_settings.restart_coordinator import RestartCoordinator

    class FakeModelService:
        attempts = 0

        def apply(self, model_id: str) -> None:
            self.attempts += 1
            if self.attempts < 3:
                raise OllamaConnectionError("starting")

    config_path = tmp_path / "config.json"
    config_path.write_text('{"models":{"gemma4:26b-mlx":{"num_ctx":16384}},"server":{}}')
    coordinator = RestartCoordinator(
        config_path,
        FakeAdapter(),
        FakeModelService(),
        sleep=lambda _: None,
    )
    coordinator.adapter.restart_ollama = lambda: RestartResult(True, "ok")  # type: ignore[attr-defined]

    result = coordinator.restart_and_reapply_profiles()

    assert result.success is True

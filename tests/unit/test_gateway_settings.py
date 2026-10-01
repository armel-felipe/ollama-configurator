from pathlib import Path

import pytest

from backend.gateway_settings import (
    DEFAULT_GATEWAY_HOST,
    GATEWAY_BIND_OPTIONS,
    GATEWAY_PORT,
    GatewaySettingsService,
)
from backend.persistence.store import ConfigStore


def service(tmp_path: Path) -> GatewaySettingsService:
    return GatewaySettingsService(ConfigStore(tmp_path / "config.json"))


def test_missing_gateway_config_defaults_to_local_bind(tmp_path: Path) -> None:
    state = service(tmp_path).get(effective_host=DEFAULT_GATEWAY_HOST)

    assert state.host == "127.0.0.1"
    assert state.effective_host == "127.0.0.1"
    assert state.port == GATEWAY_PORT
    assert state.pending_restart is False
    assert state.options == GATEWAY_BIND_OPTIONS
    assert state.warning is None


def test_network_bind_is_persisted_and_marks_restart_pending(tmp_path: Path) -> None:
    gateway_service = service(tmp_path)

    state = gateway_service.update("0.0.0.0", effective_host="127.0.0.1")

    assert state.host == "0.0.0.0"
    assert state.effective_host == "127.0.0.1"
    assert state.pending_restart is True
    assert state.warning is not None
    assert gateway_service.get(effective_host="127.0.0.1").host == "0.0.0.0"
    assert ConfigStore(tmp_path / "config.json").load()["gateway"] == {"host": "0.0.0.0"}


def test_invalid_bind_host_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="host"):
        service(tmp_path).update("192.168.1.10", effective_host=DEFAULT_GATEWAY_HOST)


def test_reset_removes_gateway_override_and_preserves_other_sections(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save({
        "models": {"gemma4:26b-mlx": {"think": False}},
        "server": {"OLLAMA_KV_CACHE_TYPE": "q8_0"},
        "gateway": {"host": "0.0.0.0"},
    })

    state = GatewaySettingsService(store).reset(effective_host="0.0.0.0")

    assert state.host == DEFAULT_GATEWAY_HOST
    assert state.effective_host == "0.0.0.0"
    assert state.pending_restart is True
    saved = store.load()
    assert "gateway" not in saved
    assert saved["models"]["gemma4:26b-mlx"]["think"] is False
    assert saved["server"]["OLLAMA_KV_CACHE_TYPE"] == "q8_0"


def test_corrupt_config_is_not_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid configuration"):
        service(tmp_path).get(effective_host=DEFAULT_GATEWAY_HOST)

    assert path.read_text(encoding="utf-8") == "not-json"

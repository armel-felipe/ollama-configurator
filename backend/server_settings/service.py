from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.logs import LOG_STORE
from backend.os_adapters.base import RestartResult, SystemAdapter
from backend.persistence.store import ConfigStore
from backend.server_settings.catalog import (
    SERVER_SETTINGS,
    parse_environment,
    public_catalog,
    validate_setting,
)


@dataclass
class ServerSettingsState:
    settings: dict[str, Any]
    effective: dict[str, Any]
    pending_restart: bool
    available: bool
    capabilities: dict[str, dict[str, Any]]


class ServerSettingsService:
    def __init__(self, config_path: Path, adapter: SystemAdapter) -> None:
        self.store = ConfigStore(config_path)
        self.adapter = adapter

    def get(self) -> ServerSettingsState:
        server = self.store.load().get("server", {})
        settings = {name: server[name] for name in SERVER_SETTINGS if name in server}
        effective: dict[str, Any] = {}
        for name, metadata in SERVER_SETTINGS.items():
            raw_value = self.adapter.get_environment(name)
            effective[name] = (
                parse_environment(name, raw_value)
                if raw_value is not None
                else settings.get(name, metadata["default"])
            )
        return ServerSettingsState(
            settings=settings,
            effective=effective,
            pending_restart=bool(server.get("_restart_pending", False)),
            available=True,
            capabilities=public_catalog(),
        )

    def update(self, patch: dict[str, Any]) -> ServerSettingsState:
        config = self.store.load()
        server = dict(config.get("server", {}))
        for name, value in patch.items():
            value = validate_setting(name, value)
            if value == "default":
                self.adapter.remove_environment(name)
                server.pop(name, None)
            else:
                self.adapter.set_environment(name, self._to_environment(value))
                server[name] = value
        server["_restart_pending"] = True
        config["server"] = server
        self.store.save(config)
        LOG_STORE.emit(
            "configurator",
            "info",
            "Configurações globais salvas",
            {key: server.get(key) for key in patch},
        )
        return self.get()

    def reset(self) -> ServerSettingsState:
        config = self.store.load()
        server = dict(config.get("server", {}))
        for name in list(SERVER_SETTINGS):
            if name in server:
                self.adapter.remove_environment(name)
        config["server"] = {"_restart_pending": True}
        self.store.save(config)
        LOG_STORE.emit("configurator", "info", "Configurações globais restauradas para padrão")
        return self.get()

    def restart(self) -> RestartResult:
        result = self.adapter.restart_ollama()
        if result.success:
            self.clear_pending()
        return result

    def clear_pending(self) -> None:
        config = self.store.load()
        server = dict(config.get("server", {}))
        server.pop("_restart_pending", None)
        config["server"] = server
        self.store.save(config)

    @staticmethod
    def _to_environment(value: Any) -> str:
        if isinstance(value, bool):
            return str(value).lower()
        return str(value)

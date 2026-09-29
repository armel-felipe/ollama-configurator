from pathlib import Path
from typing import Protocol

from backend.os_adapters.base import RestartResult, SystemAdapter
from backend.persistence.store import ConfigStore
from backend.server_settings.service import ServerSettingsService


class ModelProfileApplier(Protocol):
    def apply(self, model_id: str) -> object: ...


class RestartCoordinator:
    def __init__(
        self, config_path: Path, adapter: SystemAdapter, model_service: ModelProfileApplier
    ) -> None:
        self.config_path = config_path
        self.adapter = adapter
        self.model_service = model_service

    def restart_and_reapply_profiles(self) -> RestartResult:
        result = self.adapter.restart_ollama()
        if not result.success:
            return result
        config = ConfigStore(self.config_path).load()
        reapplied: list[str] = []
        try:
            for model_id in config.get("models", {}):
                self.model_service.apply(model_id)
                reapplied.append(model_id)
        except Exception as error:
            return RestartResult(
                False, f"Ollama reiniciado, mas falhou ao reaplicar perfis: {error}", reapplied
            )
        ServerSettingsService(self.config_path, self.adapter).clear_pending()
        return RestartResult(True, "Ollama reiniciado e perfis reaplicados", reapplied)

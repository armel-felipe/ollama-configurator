from datetime import UTC, datetime
from typing import Any

from backend.ollama.client import OllamaClient
from backend.persistence.store import ConfigStore


class RuntimeProfileService:
    def __init__(self, store: ConfigStore, client: OllamaClient) -> None:
        self.store = store
        self.client = client

    def status(self, model_id: str) -> dict[str, Any]:
        saved = dict(self.store.load().get("models", {}).get(model_id, {}))
        running = next(
            (item for item in self.client.list_running_models() if item.get("name") == model_id),
            None,
        )
        return {
            "model": model_id,
            "loaded": running is not None,
            "context": running.get("context_length") if running else None,
            "processor": (running.get("processor") or running.get("runner")) if running else None,
            "until": (running.get("until") or running.get("expires_at")) if running else None,
            "applied_options": saved,
            "observed_at": datetime.now(UTC).isoformat(),
        }

from datetime import UTC, datetime
from typing import Any, Protocol

from backend.persistence.store import ConfigStore


class RuntimeClient(Protocol):
    def list_running_models(self) -> list[dict[str, Any]]: ...


class RuntimeProfileService:
    def __init__(self, store: ConfigStore, client: RuntimeClient) -> None:
        self.store = store
        self.client = client

    def status(self, model_id: str) -> dict[str, Any]:
        saved = dict(self.store.load().get("models", {}).get(model_id, {}))
        running = next(
            (item for item in self.client.list_running_models() if item.get("name") == model_id),
            None,
        )
        requested_context = saved.get("num_ctx")
        if not isinstance(requested_context, int) or isinstance(requested_context, bool):
            requested_context = None
        effective_context = running.get("context_length") if running else None
        context_matches = (
            None
            if requested_context is None or effective_context is None
            else requested_context == effective_context
        )
        return {
            "model": model_id,
            "loaded": running is not None,
            "context": effective_context,
            "requested_context": requested_context,
            "context_matches": context_matches,
            "processor": (running.get("processor") or running.get("runner")) if running else None,
            "until": (running.get("until") or running.get("expires_at")) if running else None,
            "applied_options": saved,
            "observed_at": datetime.now(UTC).isoformat(),
        }

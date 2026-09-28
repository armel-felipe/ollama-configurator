from typing import Any

from backend.domain.settings import normalize_options
from backend.ollama.client import OllamaClient
from backend.persistence.store import ConfigStore

SUPPORTED_OPTIONS = {"num_ctx", "temperature", "num_predict", "keep_alive"}


def validate_option_patch(patch: dict[str, Any]) -> dict[str, Any]:
    for name, value in patch.items():
        if name not in SUPPORTED_OPTIONS:
            raise ValueError(f"unsupported model option: {name}")
        if value == "default":
            continue
        if name == "num_ctx" and (
            not isinstance(value, int) or isinstance(value, bool) or value < 1
        ):
            raise ValueError("num_ctx must be a positive integer")
        if name == "temperature" and (
            not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 2
        ):
            raise ValueError("temperature must be between 0 and 2")
        if name == "num_predict" and (
            not isinstance(value, int) or isinstance(value, bool) or value < -2
        ):
            raise ValueError("num_predict must be -2, -1, or a non-negative integer")
        if name == "keep_alive" and not isinstance(value, (str, int)):
            raise ValueError("keep_alive must be a duration string or integer")
    result = normalize_options(patch)
    if "temperature" in result:
        result["temperature"] = float(result["temperature"])
    return result | {name: "default" for name, value in patch.items() if value == "default"}


class ModelSettingsService:
    def __init__(self, store: ConfigStore, client: OllamaClient) -> None:
        self.store = store
        self.client = client

    def get(self, model_id: str) -> dict[str, Any]:
        config = self.store.load()
        return dict(config.get("models", {}).get(model_id, {}))

    def update(self, model_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        validated = validate_option_patch(patch)
        config = self.store.load()
        models = config.setdefault("models", {})
        current = dict(models.get(model_id, {}))
        for name, value in validated.items():
            if value == "default":
                current.pop(name, None)
            else:
                current[name] = value
        if current:
            models[model_id] = current
        else:
            models.pop(model_id, None)
        self.store.save(config)
        return current

    def reset_parameter(self, model_id: str, parameter: str) -> dict[str, Any]:
        return self.update(model_id, {parameter: "default"})

    def apply(self, model_id: str) -> dict[str, Any]:
        options = self.get(model_id)
        keep_alive = options.pop("keep_alive", None)
        return self.client.generate(model_id, options=options, keep_alive=keep_alive)

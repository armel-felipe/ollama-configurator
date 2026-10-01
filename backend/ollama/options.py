from typing import Any

from backend.domain.settings import normalize_options
from backend.ollama.client import OllamaClient
from backend.persistence.store import ConfigStore

SUPPORTED_OPTIONS = {"num_ctx", "temperature", "num_predict", "keep_alive", "think"}


def extract_model_defaults(spec: dict[str, Any]) -> dict[str, str]:
    defaults = {
        "num_ctx": "Ollama Default (dinâmico)",
        "temperature": "Ollama Default",
        "num_predict": "Ollama Default",
        "keep_alive": "Ollama Default (servidor)",
    }
    parameters = spec.get("parameters")
    if isinstance(parameters, str):
        for line in parameters.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] in {
                "temperature",
                "num_predict",
                "num_ctx",
                "keep_alive",
            }:
                defaults[parts[0]] = parts[1]
    model_info = spec.get("model_info")
    if isinstance(model_info, dict):
        context_length = next(
            (
                value
                for key, value in model_info.items()
                if key.endswith(".context_length") and isinstance(value, int)
            ),
            None,
        )
        if context_length is not None:
            defaults["num_ctx"] = f"Ollama Default (dinâmico; máximo do modelo {context_length})"
    return defaults


def validate_thinking(value: Any, spec: dict[str, Any]) -> bool | str:
    values = spec.get("values", [])
    if not isinstance(values, list) or value not in values or not isinstance(value, (bool, str)):
        raise ValueError(f"unsupported thinking value: {value}")
    return value


def validate_option_patch(patch: dict[str, Any]) -> dict[str, Any]:
    for name, value in patch.items():
        if name not in SUPPORTED_OPTIONS:
            raise ValueError(f"unsupported model option: {name}")
        if value == "default":
            continue
        if name == "think":
            if value != "default" and (not isinstance(value, (bool, str))):
                raise ValueError("think must be a boolean, level, or default")
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
        think = options.pop("think", None)
        self.client.reload_model(model_id, options, think=think, keep_alive=keep_alive)
        return options | ({"think": think} if think is not None else {})

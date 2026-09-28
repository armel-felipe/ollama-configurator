import re
from dataclasses import dataclass
from typing import Any, Protocol

from backend.ollama.runtime import RuntimeProfileService
from backend.persistence.store import ConfigStore


class InferenceClient(Protocol):
    def generate(
        self,
        model: str,
        prompt: str = "",
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> dict[str, Any]: ...

    def list_running_models(self) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class InferenceResult:
    requested_profile: dict[str, Any]
    thinking: str | None
    thinking_received: bool
    response: str
    runtime: dict[str, Any]


_THINK_TAG = re.compile(r"<think>(.*?)</think>", re.IGNORECASE | re.DOTALL)


class InferenceService:
    def __init__(self, store: ConfigStore, client: InferenceClient) -> None:
        self.store = store
        self.client = client

    def run(self, model_id: str, prompt: str) -> InferenceResult:
        clean_prompt = prompt.strip()
        if not clean_prompt:
            raise ValueError("prompt must not be blank")

        saved = dict(self.store.load().get("models", {}).get(model_id, {}))
        options = {key: value for key, value in saved.items() if key not in {"think", "keep_alive"}}
        think = saved.get("think")
        keep_alive = saved.get("keep_alive")
        data = self.client.generate(
            model_id,
            prompt=clean_prompt,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )
        response = data.get("response")
        if not isinstance(response, str):
            raise ValueError("Ollama returned an invalid inference response")

        thinking = data.get("thinking") if isinstance(data.get("thinking"), str) else None
        leaked = _THINK_TAG.search(response)
        if leaked:
            thinking = thinking or leaked.group(1).strip() or None
            response = _THINK_TAG.sub("", response).strip()

        runtime = RuntimeProfileService(self.store, self.client).status(model_id)
        return InferenceResult(
            requested_profile=saved,
            thinking=thinking,
            thinking_received=bool(thinking),
            response=response,
            runtime=runtime,
        )

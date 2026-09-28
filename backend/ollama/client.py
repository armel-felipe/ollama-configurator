from collections.abc import Callable
from typing import Any

import httpx

from backend.ollama.schemas import OllamaModel, OllamaVersion


class OllamaError(RuntimeError):
    """Base error for Ollama integration failures."""


class OllamaConnectionError(OllamaError):
    """Ollama cannot be reached."""


class OllamaResponseError(OllamaError):
    """Ollama returned an invalid response."""


Transport = httpx.BaseTransport | httpx.AsyncBaseTransport


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        transport: Transport | None = None,
        client_factory: Callable[..., httpx.Client] = httpx.Client,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._transport = transport
        self._client_factory = client_factory
        self._client = client_factory(base_url=self.base_url, timeout=5.0, transport=transport)

    def get_version(self) -> OllamaVersion:
        data = self._get_json("/api/version")
        version = data.get("version")
        if not isinstance(version, str) or not version:
            raise OllamaResponseError("Ollama version response is invalid")
        return OllamaVersion(version=version)

    def list_models(self) -> list[OllamaModel]:
        data = self._get_json("/api/tags")
        models = data.get("models")
        if not isinstance(models, list):
            raise OllamaResponseError("Ollama models response is invalid")
        normalized: list[OllamaModel] = []
        for model in models:
            if not isinstance(model, dict) or not isinstance(model.get("name"), str):
                raise OllamaResponseError("Ollama model entry is invalid")
            normalized.append(
                OllamaModel(
                    name=model["name"],
                    size=model.get("size") if isinstance(model.get("size"), int) else None,
                    details=model.get("details", {})
                    if isinstance(model.get("details", {}), dict)
                    else {},
                )
            )
        return normalized

    def show_model(self, model: str) -> dict[str, Any]:
        return self._post_json("/api/show", {"model": model})

    def list_running_models(self) -> list[dict[str, Any]]:
        data = self._get_json("/api/ps")
        models = data.get("models")
        if not isinstance(models, list):
            raise OllamaResponseError("Ollama running models response is invalid")
        return [model for model in models if isinstance(model, dict)]

    def reload_model(
        self,
        model: str,
        options: dict[str, Any],
        think: bool | str | None,
        keep_alive: str | int | None,
    ) -> None:
        self.generate(model, keep_alive=0)
        self._client.close()
        self._client = self._client_factory(
            base_url=self.base_url,
            timeout=5.0,
            transport=self._transport,
        )
        self.generate(model, options=options, think=think, keep_alive=keep_alive)

    def generate(
        self,
        model: str,
        prompt: str = "",
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options or {},
        }
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive
        if think is not None:
            payload["think"] = think
        try:
            response = self._client.post("/api/generate", json=payload, timeout=180.0)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise OllamaConnectionError("Ollama could not apply model settings") from error
        if not isinstance(data, dict):
            raise OllamaResponseError("Ollama generate response is invalid")
        return data

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options or {},
        }
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive
        if think is not None:
            payload["think"] = think
        try:
            response = self._client.post("/api/chat", json=payload, timeout=180.0)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise OllamaConnectionError("Ollama chat request failed") from error
        if not isinstance(data, dict):
            raise OllamaResponseError("Ollama chat response is invalid")
        return data

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._client.post(path, json=payload)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise OllamaConnectionError("Ollama is unavailable") from error
        if not isinstance(data, dict):
            raise OllamaResponseError("Ollama returned a non-object response")
        return data

    def _get_json(self, path: str) -> dict[str, Any]:
        try:
            response = self._client.get(path)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise OllamaConnectionError("Ollama is unavailable") from error
        if not isinstance(data, dict):
            raise OllamaResponseError("Ollama returned a non-object response")
        return data


def get_ollama_client() -> OllamaClient:
    return OllamaClient()

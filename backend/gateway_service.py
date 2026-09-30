import time
from collections.abc import Iterator
from typing import Any, Protocol
from uuid import uuid4

from backend.logs import LOG_STORE, LogStore
from backend.persistence.store import ConfigStore


class GatewayClient(Protocol):
    def generate(
        self,
        model: str,
        prompt: str = "",
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> dict[str, Any]: ...

    def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> dict[str, Any]: ...

    def generate_stream(
        self,
        model: str,
        prompt: str = "",
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> Iterator[dict[str, Any]]: ...

    def chat_stream(
        self,
        model: str,
        messages: list[dict[str, Any]],
        options: dict[str, Any] | None = None,
        keep_alive: str | int | None = None,
        think: bool | str | None = None,
    ) -> Iterator[dict[str, Any]]: ...


class GatewayService:
    def __init__(
        self,
        store: ConfigStore,
        client: GatewayClient,
        log_store: LogStore = LOG_STORE,
    ) -> None:
        self.store = store
        self.client = client
        self.log_store = log_store

    def generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        model, options, think, keep_alive = self._profile(payload)
        if payload.get("stream", False):
            raise ValueError("streaming is not supported by the gateway yet")
        prompt = payload.get("prompt", "")
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")
        return self.client.generate(
            model,
            prompt=prompt,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        model, options, think, keep_alive = self._profile(payload)
        if payload.get("stream", False):
            raise ValueError("streaming is not supported by the gateway yet")
        messages = self._messages(payload)
        result = self.client.chat(
            model,
            messages,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )
        message = result.get("message")
        if not isinstance(message, dict):
            raise ValueError("Ollama chat response is invalid")
        choice_message: dict[str, Any] = {
            "role": message.get("role", "assistant"),
            "content": message.get("content", ""),
        }
        if isinstance(message.get("thinking"), str):
            choice_message["reasoning_content"] = message["thinking"]
        return {
            "id": f"chatcmpl-{uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{"index": 0, "message": choice_message, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": (result.get("prompt_eval_count", 0) or 0)
                + (result.get("eval_count", 0) or 0),
            },
        }

    def stream_generate(self, payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
        model, options, think, keep_alive = self._profile(payload)
        prompt = payload.get("prompt", "")
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")
        yield from self.client.generate_stream(
            model,
            prompt=prompt,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )

    def chat_ollama(self, payload: dict[str, Any]) -> dict[str, Any]:
        model, options, think, keep_alive = self._profile(payload)
        messages = self._messages(payload)
        if payload.get("stream", False):
            raise ValueError("use stream_chat_ollama for streaming")
        return self.client.chat(
            model,
            messages,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )

    def stream_chat_ollama(self, payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
        model, options, think, keep_alive = self._profile(payload)
        messages = self._messages(payload)
        yield from self.client.chat_stream(
            model,
            messages,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )

    def stream_chat(self, payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
        model, options, think, keep_alive = self._profile(payload)
        messages = self._messages(payload)
        stream_id = f"chatcmpl-{uuid4().hex}"
        created = int(time.time())
        for result in self.client.chat_stream(
            model,
            messages,
            options=options,
            think=think,
            keep_alive=keep_alive,
        ):
            message = result.get("message")
            if not isinstance(message, dict):
                raise ValueError("Ollama chat stream chunk is invalid")
            delta: dict[str, Any] = {}
            if isinstance(message.get("role"), str):
                delta["role"] = message["role"]
            if isinstance(message.get("content"), str):
                delta["content"] = message["content"]
            if isinstance(message.get("thinking"), str):
                delta["reasoning_content"] = message["thinking"]
            chunk: dict[str, Any] = {
                "id": stream_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{
                    "index": 0,
                    "delta": delta,
                    "finish_reason": "stop" if result.get("done") else None,
                }],
            }
            if result.get("done"):
                prompt_tokens = result.get("prompt_eval_count", 0) or 0
                completion_tokens = result.get("eval_count", 0) or 0
                chunk["usage"] = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }
            yield chunk

    def _profile(
        self, payload: dict[str, Any]
    ) -> tuple[str, dict[str, Any], bool | str | None, str | int | None]:
        model = payload.get("model")
        if not isinstance(model, str) or not model:
            raise ValueError("model must be a non-empty string")
        saved = dict(self.store.load().get("models", {}).get(model, {}))
        incoming_options = payload.get("options", {})
        if not isinstance(incoming_options, dict):
            raise ValueError("options must be an object")
        options = dict(incoming_options)
        options.update(
            {key: value for key, value in saved.items() if key not in {"think", "keep_alive"}}
        )
        think = saved.get("think", payload.get("think"))
        keep_alive = saved.get("keep_alive", payload.get("keep_alive"))
        server = self.store.load().get("server", {})
        metadata = {
            "model": model,
            "think": think,
            "num_ctx": options.get("num_ctx"),
            "kv_cache": server.get("OLLAMA_KV_CACHE_TYPE"),
            "stream": bool(payload.get("stream", False)),
        }
        self.log_store.emit("gateway", "info", "Perfil aplicado à requisição", metadata)
        return model, options, think, keep_alive

    @staticmethod
    def _messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
        messages = payload.get("messages")
        if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
            raise ValueError("messages must be a list of objects")
        normalized: list[dict[str, Any]] = []
        for item in messages:
            message = dict(item)
            content = message.get("content")
            if isinstance(content, list):
                message["content"] = "".join(
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict) and isinstance(part.get("text"), str)
                )
            elif content is not None and not isinstance(content, str):
                raise ValueError("message content must be a string or text parts")
            normalized.append(message)
        return normalized

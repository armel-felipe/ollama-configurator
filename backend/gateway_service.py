import time
from collections.abc import Iterator
from typing import Any, Protocol
from uuid import uuid4

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
    def __init__(self, store: ConfigStore, client: GatewayClient) -> None:
        self.store = store
        self.client = client

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
        messages = payload.get("messages")
        if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
            raise ValueError("messages must be a list of objects")
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
        messages = payload.get("messages")
        if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
            raise ValueError("messages must be a list of objects")
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
        messages = payload.get("messages")
        if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
            raise ValueError("messages must be a list of objects")
        yield from self.client.chat_stream(
            model,
            messages,
            options=options,
            think=think,
            keep_alive=keep_alive,
        )

    def stream_chat(self, payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
        model, options, think, keep_alive = self._profile(payload)
        messages = payload.get("messages")
        if not isinstance(messages, list) or not all(isinstance(item, dict) for item in messages):
            raise ValueError("messages must be a list of objects")
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
            yield {
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
        return model, options, think, keep_alive

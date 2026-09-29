from pathlib import Path

from backend.gateway_service import GatewayService
from backend.persistence.store import ConfigStore


def test_gateway_saved_values_override_client_values() -> None:
    class FakeClient:
        def generate(self, _model: str, **kwargs: object) -> dict[str, object]:
            return kwargs

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **kwargs: object
        ) -> dict[str, object]:
            return kwargs

    store = ConfigStore(Path("/tmp/gateway-test-config.json"))
    store.save({
        "models": {"gemma4:26b-mlx": {"num_ctx": 16384, "temperature": 0.7, "think": False}},
        "server": {},
    })
    service = GatewayService(store, FakeClient())

    result = service.generate(
        {
            "model": "gemma4:26b-mlx",
            "prompt": "teste",
            "options": {"num_ctx": 4096, "temperature": 1.2, "num_predict": 100},
            "think": True,
            "stream": False,
        }
    )

    assert result["options"] == {"num_ctx": 16384, "temperature": 0.7, "num_predict": 100}
    assert result["think"] is False
    assert result["prompt"] == "teste"


def test_gateway_keeps_client_values_when_profile_is_default() -> None:
    class FakeClient:
        def generate(self, _model: str, **kwargs: object) -> dict[str, object]:
            return kwargs

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **kwargs: object
        ) -> dict[str, object]:
            return kwargs

    store = ConfigStore(Path("/tmp/gateway-default-config.json"))
    store.save({"models": {"qwen:latest": {}}, "server": {}})
    service = GatewayService(store, FakeClient())

    result = service.generate(
        {
            "model": "qwen:latest",
            "prompt": "teste",
            "options": {"temperature": 0.2},
            "stream": False,
        }
    )

    assert result["options"] == {"temperature": 0.2}
    assert result["think"] is None


def test_gateway_converts_openai_chat_to_ollama_response() -> None:
    class FakeClient:
        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {}

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **kwargs: object
        ) -> dict[str, object]:
            assert kwargs["think"] is False
            return {"message": {"role": "assistant", "content": "Resposta"}, "done": True}

    store = ConfigStore(Path("/tmp/gateway-chat-config.json"))
    store.save({"models": {"qwen:latest": {"think": False}}, "server": {}})
    service = GatewayService(store, FakeClient())

    result = service.chat(
        {
            "model": "qwen:latest",
            "messages": [{"role": "user", "content": "Oi"}],
            "stream": False,
        }
    )

    assert result["choices"][0]["message"] == {"role": "assistant", "content": "Resposta"}
    assert result["model"] == "qwen:latest"


def test_gateway_stream_generate_forwards_saved_profile() -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {}

        def chat(
            self, _model: str, _messages: list[dict[str, object]], **_: object
        ) -> dict[str, object]:
            return {}

        def generate_stream(self, _model: str, **kwargs: object):
            captured.update(kwargs)
            yield {"response": "Olá", "done": False}
            yield {"response": " mundo", "done": True}

    store = ConfigStore(Path("/tmp/gateway-stream-config.json"))
    store.save({"models": {"gemma4:26b-mlx": {"num_ctx": 16384, "think": False}}, "server": {}})
    service = GatewayService(store, FakeClient())

    chunks = list(service.stream_generate({
        "model": "gemma4:26b-mlx",
        "prompt": "Oi",
        "stream": True,
        "options": {"num_ctx": 4096},
        "think": True,
    }))

    assert captured["think"] is False
    assert captured["options"] == {"num_ctx": 16384}
    assert chunks[-1]["done"] is True


def test_openai_stream_includes_usage_on_final_chunk() -> None:
    class FakeClient:
        def chat_stream(self, _model: str, _messages: list[dict[str, object]], **_: object):
            yield {"message": {"role": "assistant", "content": "Olá"}, "done": False}
            yield {
                "message": {"role": "assistant", "content": ""},
                "done": True,
                "prompt_eval_count": 12,
                "eval_count": 7,
            }

    store = ConfigStore(Path("/tmp/gateway-stream-usage-config.json"))
    service = GatewayService(store, FakeClient())

    chunks = list(
        service.stream_chat(
            {
                "model": "gemma4:26b-mlx",
                "messages": [{"role": "user", "content": "Oi"}],
                "stream": True,
            }
        )
    )

    assert chunks[-1]["usage"] == {
        "prompt_tokens": 12,
        "completion_tokens": 7,
        "total_tokens": 19,
    }

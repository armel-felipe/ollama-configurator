from pathlib import Path

from backend.inference.service import InferenceService
from backend.persistence.store import ConfigStore


def test_run_sends_saved_profile_and_returns_thinking_separately(tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def generate(
            self,
            model: str,
            prompt: str,
            options: dict[str, object],
            think: bool | str | None,
            keep_alive: str | int | None,
        ) -> dict[str, object]:
            captured.update(
                model=model, prompt=prompt, options=options, think=think, keep_alive=keep_alive
            )
            return {"response": "Resposta final", "thinking": "Raciocínio interno", "done": True}

        def list_running_models(self) -> list[dict[str, object]]:
            return [{"name": "gemma4:26b-mlx", "context_length": 16384}]

    store = ConfigStore(tmp_path / "config.json")
    store.save(
        {
            "models": {
                "gemma4:26b-mlx": {
                    "num_ctx": 16384,
                    "temperature": 0.7,
                    "think": False,
                    "keep_alive": "10m",
                }
            },
            "server": {},
        }
    )

    result = InferenceService(store, FakeClient()).run(
        "gemma4:26b-mlx", "Quem foi o 23º presidente do Brasil?"
    )

    assert captured == {
        "model": "gemma4:26b-mlx",
        "prompt": "Quem foi o 23º presidente do Brasil?",
        "options": {"num_ctx": 16384, "temperature": 0.7},
        "think": False,
        "keep_alive": "10m",
    }
    assert result.requested_profile == {
        "num_ctx": 16384,
        "temperature": 0.7,
        "think": False,
        "keep_alive": "10m",
    }
    assert result.thinking == "Raciocínio interno"
    assert result.response == "Resposta final"
    assert result.runtime["context"] == 16384


def test_run_extracts_leaked_think_tags_from_final_response(tmp_path: Path) -> None:
    class FakeClient:
        def generate(self, _model: str, **_: object) -> dict[str, object]:
            return {"response": "<think>oculto</think>Resposta limpa", "done": True}

        def list_running_models(self) -> list[dict[str, object]]:
            return []

    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"qwen:latest": {"think": False}}, "server": {}})

    result = InferenceService(store, FakeClient()).run("qwen:latest", "teste")

    assert result.thinking == "oculto"
    assert result.response == "Resposta limpa"
    assert result.thinking_received is True


def test_run_preserves_named_thinking_level(tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def generate(self, _model: str, **kwargs: object) -> dict[str, object]:
            captured.update(kwargs)
            return {"response": "ok", "done": True}

        def list_running_models(self) -> list[dict[str, object]]:
            return []

    store = ConfigStore(tmp_path / "config.json")
    store.save({"models": {"qwen:latest": {"think": "high", "num_ctx": 32768}}, "server": {}})

    result = InferenceService(store, FakeClient()).run("qwen:latest", "teste")

    assert captured["think"] == "high"
    assert result.thinking_received is False

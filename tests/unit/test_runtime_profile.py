import httpx

from backend.ollama.client import OllamaClient
from backend.ollama.options import extract_model_defaults, validate_thinking


def test_reads_model_thinking_spec_and_running_context() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/show":
            return httpx.Response(
                200, json={"thinking": {"values": [False, "low", "high"], "default": "low"}}
            )
        if request.url.path == "/api/ps":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {"name": "qwen:latest", "context_length": 65536, "processor": "100% GPU"}
                    ]
                },
            )
        raise AssertionError(request.url.path)

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))

    assert client.show_model("qwen:latest")["thinking"]["default"] == "low"
    assert client.list_running_models()[0]["context_length"] == 65536


def test_thinking_must_be_declared_by_model() -> None:
    spec = {"values": [False, "low", "high"], "default": "low"}

    assert validate_thinking("high", spec) == "high"
    assert validate_thinking(False, spec) is False

    try:
        validate_thinking("medium", spec)
    except ValueError as error:
        assert "unsupported thinking value" in str(error)
    else:
        raise AssertionError("unsupported thinking value was accepted")


def test_extracts_declared_defaults_and_dynamic_context_limit() -> None:
    defaults = extract_model_defaults(
        {
            "parameters": "temperature 1\ntop_k 20",
            "model_info": {"qwen.context_length": 262144},
        }
    )

    assert defaults["temperature"] == "1"
    assert "262144" in defaults["num_ctx"]
    assert defaults["keep_alive"] == "Ollama Default (servidor)"


def test_reload_unloads_before_loading_new_profile() -> None:
    requests: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path != "/api/generate":
            raise AssertionError(request.url.path)
        requests.append(__import__("json").loads(request.content))
        return httpx.Response(200, json={"response": "", "done": True})

    client = OllamaClient("http://ollama", transport=httpx.MockTransport(handler))
    client.reload_model("qwen:latest", {"num_ctx": 65536}, "high", "30m")

    assert requests[0]["keep_alive"] == 0
    assert requests[1]["options"] == {"num_ctx": 65536}
    assert requests[1]["think"] == "high"
    assert requests[1]["keep_alive"] == "30m"

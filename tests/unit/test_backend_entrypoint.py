from __future__ import annotations

from collections.abc import Iterator
from email.message import Message

import pytest

import backend.__main__ as entrypoint


class _HealthyResponse:
    status = 200
    headers = Message()
    headers["Content-Type"] = "text/html"

    def __enter__(self) -> _HealthyResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_browser_opens_only_after_health_check_succeeds(monkeypatch) -> None:
    attempts = 0

    def fake_urlopen(_url: str, timeout: float) -> _HealthyResponse:
        nonlocal attempts
        assert timeout == 0.5
        attempts += 1
        if attempts < 3:
            raise OSError("server is not ready")
        return _HealthyResponse()

    clock: Iterator[float] = iter((0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    opened: list[str] = []
    monkeypatch.setattr(entrypoint, "urlopen", fake_urlopen)
    monkeypatch.setattr(entrypoint.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(entrypoint.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(entrypoint.webbrowser, "open", opened.append)

    entrypoint._open_browser_when_ready(
        "http://127.0.0.1:8787/",
        health_url="http://127.0.0.1:8787/api/health",
    )

    assert attempts == 4
    assert opened == ["http://127.0.0.1:8787/"]


def test_browser_does_not_open_when_only_api_is_available(monkeypatch) -> None:
    def respond(url, timeout):
        if url.endswith("/api/health"):
            return _HealthyResponse()
        raise OSError("404 Not Found")

    clock = iter((0.0, 0.0, 21.0))
    opened = []
    monkeypatch.setattr(entrypoint, "urlopen", respond)
    monkeypatch.setattr(entrypoint.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(entrypoint.time, "sleep", lambda _: None)
    monkeypatch.setattr(entrypoint.webbrowser, "open", opened.append)
    entrypoint._open_browser_when_ready(
        "http://127.0.0.1:8787/", health_url="http://127.0.0.1:8787/api/health"
    )
    assert opened == []


def test_port_conflict_never_starts_browser_or_application(monkeypatch) -> None:
    events = []

    def occupied(_host, _port):
        raise entrypoint.StartupError("occupied")

    monkeypatch.setenv("OLLAMA_CONFIGURATOR_OPEN_BROWSER", "1")
    monkeypatch.setattr(entrypoint, "acquire_listener", occupied)
    monkeypatch.setattr(entrypoint.threading, "Thread", lambda **kw: events.append("browser"))
    monkeypatch.setattr(entrypoint.uvicorn.Server, "run", lambda *a, **kw: events.append("server"))
    with pytest.raises(entrypoint.StartupError):
        entrypoint._run_application()
    assert events == []

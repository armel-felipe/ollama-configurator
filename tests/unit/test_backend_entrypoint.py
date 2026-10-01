from __future__ import annotations

from collections.abc import Iterator

import backend.__main__ as entrypoint


class _HealthyResponse:
    status = 200

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

    assert attempts == 3
    assert opened == ["http://127.0.0.1:8787/"]

import signal
import subprocess
from pathlib import Path

from scripts.dev import _spawn_child, _terminate_child


class FakeProcess:
    pid = 4242

    def __init__(self) -> None:
        self.terminated = False
        self.wait_calls = 0

    def poll(self) -> int | None:
        return None

    def terminate(self) -> None:
        self.terminated = True

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls += 1
        if self.wait_calls == 1:
            raise subprocess.TimeoutExpired("child", timeout)
        return 0

    def kill(self) -> None:
        self.terminated = True


def test_spawn_child_creates_a_new_process_group(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return FakeProcess()

    monkeypatch.setattr("scripts.dev.subprocess.Popen", fake_popen)

    _spawn_child(["vite"], Path("/tmp"), {})

    assert captured["start_new_session"] is True


def test_terminate_child_stops_the_entire_process_group(monkeypatch) -> None:
    process = FakeProcess()
    signals: list[tuple[int, int]] = []
    monkeypatch.setattr("scripts.dev.os.killpg", lambda pid, sig: signals.append((pid, sig)))

    _terminate_child(process)

    assert signals == [(4242, signal.SIGTERM), (4242, signal.SIGKILL)]
    assert process.wait_calls == 2

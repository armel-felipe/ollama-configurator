from pathlib import Path

import backend.gateway_manager as gateway_manager_module
from backend.gateway_manager import GatewayProcessManager


class FakeProcess:
    pid = 4242

    def __init__(self) -> None:
        self.return_code: int | None = None
        self.terminated = False

    def poll(self) -> int | None:
        return self.return_code

    def terminate(self) -> None:
        self.terminated = True
        self.return_code = 0

    def wait(self, timeout: float | None = None) -> int:
        return self.return_code or 0

    def kill(self) -> None:
        self.return_code = -9


def test_start_launches_managed_gateway_on_default_port(tmp_path: Path) -> None:
    process = FakeProcess()
    commands: list[list[str]] = []
    manager = GatewayProcessManager(
        root=tmp_path,
        process_factory=lambda command, cwd: commands.append(command) or process,
        health_checker=lambda: False,
    )

    status = manager.start()

    assert status.state == "starting"
    assert status.pid == 4242
    assert commands[0][-5:] == ["backend.gateway:app", "--host", "127.0.0.1", "--port", "11435"]


def test_frozen_app_launches_gateway_through_its_gateway_mode(
    tmp_path: Path, monkeypatch
) -> None:
    process = FakeProcess()
    commands: list[list[str]] = []
    monkeypatch.setattr(gateway_manager_module.sys, "frozen", True, raising=False)
    monkeypatch.setattr(gateway_manager_module.sys, "executable", "/app/OllamaConfiguratorBackend")
    manager = GatewayProcessManager(
        root=tmp_path,
        process_factory=lambda command, cwd: commands.append(command) or process,
        health_checker=lambda: False,
    )

    manager.start()

    assert commands == [[
        "/app/OllamaConfiguratorBackend",
        "--gateway",
        "--host",
        "127.0.0.1",
        "--port",
        "11435",
    ]]


def test_status_reports_unmanaged_listener_without_claiming_ownership(tmp_path: Path) -> None:
    manager = GatewayProcessManager(
        root=tmp_path,
        health_checker=lambda: True,
        external_process=lambda: (4242, "ollama"),
    )

    status = manager.status()

    assert status.state == "external"
    assert status.pid == 4242
    assert status.process == "ollama"
    assert "processo" in status.detail.lower()


def test_release_external_listener_terminates_only_identified_process(tmp_path: Path) -> None:
    signals: list[tuple[int, int]] = []
    manager = GatewayProcessManager(
        root=tmp_path,
        health_checker=lambda: True,
        external_process=lambda: (4242, "ollama"),
        signal_sender=lambda pid, signal: signals.append((pid, signal)),
    )

    status = manager.release_external()

    assert status.state == "stopped"
    assert signals and signals[0][0] == 4242


def test_stop_terminates_only_the_managed_process(tmp_path: Path) -> None:
    process = FakeProcess()
    manager = GatewayProcessManager(
        root=tmp_path,
        process_factory=lambda command, cwd: process,
        health_checker=lambda: False,
    )
    manager.start()

    status = manager.stop()

    assert process.terminated is True
    assert status.state == "stopped"

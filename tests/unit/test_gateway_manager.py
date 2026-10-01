from pathlib import Path

import backend.gateway_manager as gateway_manager_module
from backend.gateway_manager import GatewayProcessManager, _external_process, _health_check


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


def test_start_launches_network_gateway_when_host_is_configured(tmp_path: Path) -> None:
    process = FakeProcess()
    commands: list[list[str]] = []
    manager = GatewayProcessManager(
        root=tmp_path,
        host="0.0.0.0",
        process_factory=lambda command, cwd: commands.append(command) or process,
        health_checker=lambda: False,
    )

    manager.start()

    assert commands[0][-5:] == ["backend.gateway:app", "--host", "0.0.0.0", "--port", "11435"]


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


def test_start_releases_dedicated_port_before_launching_gateway(tmp_path: Path) -> None:
    process = FakeProcess()
    signals: list[tuple[int, int]] = []
    listener_present = True

    def external_process() -> tuple[int, str] | None:
        return (4242, "OllamaConfigurator") if listener_present else None

    def release(pid: int, signal: int) -> None:
        nonlocal listener_present
        signals.append((pid, signal))
        listener_present = False

    manager = GatewayProcessManager(
        root=tmp_path,
        host="0.0.0.0",
        process_factory=lambda command, cwd: process,
        health_checker=lambda: listener_present,
        external_process=external_process,
        signal_sender=release,
    )

    status = manager.start()

    assert status.state == "starting"
    assert signals and signals[0][0] == 4242
    assert process.pid == status.pid


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


def test_restart_terminates_previous_process_before_starting_new_host(tmp_path: Path) -> None:
    processes = [FakeProcess(), FakeProcess()]
    commands: list[list[str]] = []
    manager = GatewayProcessManager(
        root=tmp_path,
        process_factory=lambda command, cwd: commands.append(command) or processes.pop(0),
        health_checker=lambda: False,
    )

    manager.start()
    restarted = manager.restart(host="0.0.0.0")

    assert restarted.host == "0.0.0.0"
    assert commands[-1][-5:] == ["backend.gateway:app", "--host", "0.0.0.0", "--port", "11435"]
    assert len(processes) == 0


def test_wildcard_health_check_probes_loopback(monkeypatch) -> None:
    calls: list[str] = []

    class Response:
        is_success = True

    def fake_get(url: str, timeout: float) -> Response:
        calls.append(url)
        return Response()

    monkeypatch.setattr(gateway_manager_module.httpx, "get", fake_get)

    assert _health_check("0.0.0.0", 11435) is True
    assert calls == ["http://127.0.0.1:11435/health"]


def test_wildcard_external_process_scan_uses_port_wide_listener(monkeypatch) -> None:
    class Result:
        stdout = "p4242\ncOllama"

    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return Result()

    monkeypatch.setattr(gateway_manager_module.subprocess, "run", fake_run)

    assert _external_process("0.0.0.0", 11435) == (4242, "Ollama")
    assert "-iTCP:11435" in calls[0]


def test_status_reports_error_after_child_exits(tmp_path: Path) -> None:
    process = FakeProcess()
    manager = GatewayProcessManager(
        root=tmp_path,
        process_factory=lambda command, cwd: process,
        health_checker=lambda: False,
    )
    manager.start()
    process.return_code = 3

    status = manager.status()

    assert status.state == "error"
    assert "código 3" in (status.detail or "")

import subprocess
from pathlib import Path

from backend.os_adapters.macos import MacOSAdapter


def test_macos_adapter_persists_environment_in_managed_launch_agent(tmp_path: Path) -> None:
    commands: list[list[str]] = []
    adapter = MacOSAdapter(
        launch_agent_path=tmp_path / "com.ollama.configurator.environment.plist",
        command_runner=lambda command: commands.append(command),
    )

    adapter.set_environment("OLLAMA_KV_CACHE_TYPE", "q8_0")

    plist = (tmp_path / "com.ollama.configurator.environment.plist").read_text()
    assert "OLLAMA_KV_CACHE_TYPE" in plist
    assert "q8_0" in plist
    assert any(command[:2] == ["/bin/launchctl", "setenv"] for command in commands)


def test_macos_adapter_removes_override_and_restart_is_controlled(tmp_path: Path) -> None:
    commands: list[list[str]] = []
    adapter = MacOSAdapter(
        launch_agent_path=tmp_path / "managed.plist",
        command_runner=lambda command: commands.append(command),
    )
    adapter.set_environment("OLLAMA_FLASH_ATTENTION", "true")
    adapter.remove_environment("OLLAMA_FLASH_ATTENTION")

    result = adapter.restart_ollama()

    assert result.success is True
    assert any(command[:2] == ["/bin/launchctl", "unsetenv"] for command in commands)
    assert ["/usr/bin/osascript", "-e", 'tell application "Ollama" to quit'] in commands
    assert ["/usr/bin/open", "-a", "Ollama"] in commands


def test_macos_adapter_reports_permission_failure(tmp_path: Path) -> None:
    def denied(_: list[str]) -> None:
        raise PermissionError("denied")

    adapter = MacOSAdapter(launch_agent_path=tmp_path / "managed.plist", command_runner=denied)

    result = adapter.restart_ollama()

    assert result.success is False
    assert "denied" in result.detail


def test_macos_adapter_falls_back_when_applescript_quit_is_rejected(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def runner(command: list[str]) -> None:
        commands.append(command)
        if command[0] == "/usr/bin/osascript":
            raise subprocess.CalledProcessError(1, command)

    adapter = MacOSAdapter(launch_agent_path=tmp_path / "managed.plist", command_runner=runner)

    result = adapter.restart_ollama()

    assert result.success is True
    assert ["/usr/bin/killall", "Ollama"] in commands
    assert ["/usr/bin/open", "-a", "Ollama"] in commands


def test_macos_adapter_falls_back_to_app_bundle_when_named_open_is_rejected(tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def runner(command: list[str]) -> None:
        commands.append(command)
        if command[:3] == ["/usr/bin/open", "-a", "Ollama"]:
            raise subprocess.CalledProcessError(1, command)

    adapter = MacOSAdapter(launch_agent_path=tmp_path / "managed.plist", command_runner=runner)

    result = adapter.restart_ollama()

    assert result.success is True
    assert ["/usr/bin/open", "/Applications/Ollama.app"] in commands

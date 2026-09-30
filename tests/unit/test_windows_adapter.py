import subprocess

from backend.os_adapters.windows import WindowsAdapter


class FakeUserEnvironment:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def get(self, name: str) -> str | None:
        return self.values.get(name)

    def set(self, name: str, value: str) -> None:
        self.values[name] = value

    def remove(self, name: str) -> None:
        self.values.pop(name, None)


def test_windows_adapter_persists_user_environment_and_updates_process_environment() -> None:
    registry = FakeUserEnvironment()
    adapter = WindowsAdapter(registry=registry, command_runner=lambda _: None)

    adapter.set_environment("OLLAMA_KV_CACHE_TYPE", "q8_0")

    assert registry.values == {"OLLAMA_KV_CACHE_TYPE": "q8_0"}
    assert adapter.get_environment("OLLAMA_KV_CACHE_TYPE") == "q8_0"


def test_windows_adapter_removes_override_and_restarts_ollama() -> None:
    registry = FakeUserEnvironment()
    commands: list[list[str]] = []
    adapter = WindowsAdapter(registry=registry, command_runner=commands.append)
    adapter.set_environment("OLLAMA_FLASH_ATTENTION", "true")
    adapter.remove_environment("OLLAMA_FLASH_ATTENTION")

    result = adapter.restart_ollama()

    assert result.success is True
    assert registry.values == {}
    assert ["taskkill", "/IM", "Ollama.exe", "/T", "/F"] in commands
    assert ["cmd.exe", "/c", "start", "", "Ollama"] in commands


def test_windows_adapter_ignores_missing_ollama_process_during_restart() -> None:
    commands: list[list[str]] = []

    def runner(command: list[str]) -> None:
        commands.append(command)
        if command[0] == "taskkill":
            raise subprocess.CalledProcessError(128, command)

    adapter = WindowsAdapter(registry=FakeUserEnvironment(), command_runner=runner)

    result = adapter.restart_ollama()

    assert result.success is True
    assert ["cmd.exe", "/c", "start", "", "Ollama"] in commands


def test_windows_adapter_reports_permission_failure() -> None:
    def denied(_: list[str]) -> None:
        raise PermissionError("denied")

    adapter = WindowsAdapter(registry=FakeUserEnvironment(), command_runner=denied)

    result = adapter.restart_ollama()

    assert result.success is False
    assert "denied" in result.detail

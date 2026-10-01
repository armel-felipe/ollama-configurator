import os
import subprocess
from collections.abc import Callable
from typing import Any, Protocol

from backend.os_adapters.base import RestartResult

CommandRunner = Callable[[list[str]], None]


class UserEnvironment(Protocol):
    def get(self, name: str) -> str | None: ...

    def set(self, name: str, value: str) -> None: ...

    def remove(self, name: str) -> None: ...


def _run_command(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True, text=True)


class WindowsRegistryEnvironment:
    """Read and write persistent per-user environment values in HKCU."""

    key_path = r"Environment"

    def __init__(self) -> None:
        try:
            import winreg
        except ImportError as error:  # pragma: no cover - only used off Windows
            raise RuntimeError("o adaptador Windows só pode ser usado no Windows") from error
        self._winreg: Any = winreg

    def get(self, name: str) -> str | None:
        try:
            with self._winreg.OpenKey(self._winreg.HKEY_CURRENT_USER, self.key_path) as key:
                value, _ = self._winreg.QueryValueEx(key, name)
                return str(value)
        except FileNotFoundError:
            return None

    def set(self, name: str, value: str) -> None:
        with self._winreg.OpenKey(
            self._winreg.HKEY_CURRENT_USER,
            self.key_path,
            0,
            self._winreg.KEY_SET_VALUE,
        ) as key:
            self._winreg.SetValueEx(key, name, 0, self._winreg.REG_SZ, value)

    def remove(self, name: str) -> None:
        try:
            with self._winreg.OpenKey(
                self._winreg.HKEY_CURRENT_USER,
                self.key_path,
                0,
                self._winreg.KEY_SET_VALUE,
            ) as key:
                self._winreg.DeleteValue(key, name)
        except FileNotFoundError:
            return


class WindowsAdapter:
    """Persist Ollama overrides for the current Windows user."""

    def __init__(
        self,
        registry: UserEnvironment | None = None,
        command_runner: CommandRunner = _run_command,
    ) -> None:
        self._registry = registry or WindowsRegistryEnvironment()
        self._run = command_runner

    def get_environment(self, name: str) -> str | None:
        return self._registry.get(name)

    def set_environment(self, name: str, value: str) -> None:
        self._registry.set(name, value)
        os.environ[name] = value

    def remove_environment(self, name: str) -> None:
        self._registry.remove(name)
        os.environ.pop(name, None)

    def restart_ollama(self) -> RestartResult:
        try:
            try:
                self._run(["taskkill", "/IM", "Ollama.exe", "/T", "/F"])
            except subprocess.CalledProcessError as error:
                # taskkill returns 128 when no process matched. Starting the
                # desktop app is still the correct recovery path in that case.
                if error.returncode != 128:
                    raise
            self._run(["cmd.exe", "/c", "start", "", "Ollama"])
        except (OSError, subprocess.SubprocessError) as error:
            return RestartResult(False, f"Não foi possível reiniciar o Ollama: {error}")
        return RestartResult(True, "Ollama reiniciado; aguardando nova disponibilidade")

    def open_logs(self) -> None:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        self._run(["explorer.exe", os.path.join(local_app_data, "Ollama")])

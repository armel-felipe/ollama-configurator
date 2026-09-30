import os
import plistlib
import shlex
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from backend.os_adapters.base import RestartResult

CommandRunner = Callable[[list[str]], None]


def _run_command(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True, text=True)


class MacOSAdapter:
    """Persist Ollama environment overrides in a per-user managed LaunchAgent."""

    label = "com.ollama.configurator.environment"

    def __init__(
        self,
        launch_agent_path: Path | None = None,
        command_runner: CommandRunner = _run_command,
    ) -> None:
        default_path = Path.home() / "Library" / "LaunchAgents" / f"{self.label}.plist"
        self.launch_agent_path = launch_agent_path or default_path
        self._run = command_runner

    def get_environment(self, name: str) -> str | None:
        return self._load_environment().get(name)

    def set_environment(self, name: str, value: str) -> None:
        environment = self._load_environment()
        environment[name] = value
        self._write_environment(environment)
        self._run(["/bin/launchctl", "setenv", name, value])

    def remove_environment(self, name: str) -> None:
        environment = self._load_environment()
        environment.pop(name, None)
        if environment:
            self._write_environment(environment)
        else:
            self.launch_agent_path.unlink(missing_ok=True)
            self._helper_path.unlink(missing_ok=True)
        self._run(["/bin/launchctl", "unsetenv", name])

    def restart_ollama(self) -> RestartResult:
        try:
            quit_command = ["/usr/bin/osascript", "-e", 'tell application "Ollama" to quit']
            try:
                self._run(quit_command)
            except subprocess.CalledProcessError:
                # Some Ollama desktop versions reject AppleScript quit even
                # while the app is running. Fall back to the process name so
                # environment changes can still be applied on restart.
                self._run(["/usr/bin/killall", "Ollama"])
            try:
                self._run(["/usr/bin/open", "-a", "Ollama"])
            except subprocess.CalledProcessError:
                self._run(["/usr/bin/open", "/Applications/Ollama.app"])
        except (OSError, subprocess.SubprocessError) as error:
            return RestartResult(False, f"Não foi possível reiniciar o Ollama: {error}")
        return RestartResult(True, "Ollama reiniciado; aguardando nova disponibilidade")

    def open_logs(self) -> None:
        self._run(["/usr/bin/open", "-a", "Console"])

    def _load_environment(self) -> dict[str, str]:
        if not self.launch_agent_path.exists():
            return {}
        try:
            raw = plistlib.loads(self.launch_agent_path.read_bytes())
        except (OSError, plistlib.InvalidFileException) as error:
            raise ValueError("managed Ollama LaunchAgent is invalid") from error
        values = raw.get("EnvironmentVariables", {})
        if not isinstance(values, dict):
            raise ValueError("managed Ollama LaunchAgent has invalid environment")
        return {str(key): str(value) for key, value in values.items()}

    def _write_environment(self, environment: dict[str, str]) -> None:
        helper_path = self._helper_path
        helper_path.write_text(
            "#!/bin/zsh\n"
            + "\n".join(
                f"/bin/launchctl setenv {shlex.quote(name)} {shlex.quote(value)}"
                for name, value in sorted(environment.items())
            )
            + "\n",
            encoding="utf-8",
        )
        helper_path.chmod(0o700)
        payload: dict[str, Any] = {
            "Label": self.label,
            "ProgramArguments": ["/bin/zsh", str(helper_path)],
            "EnvironmentVariables": environment,
            "RunAtLoad": True,
        }
        self.launch_agent_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            dir=self.launch_agent_path.parent, prefix=".ollama-"
        )
        try:
            with os.fdopen(descriptor, "wb") as file:
                plistlib.dump(payload, file)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.launch_agent_path)
        except Exception:
            Path(temporary).unlink(missing_ok=True)
            raise

    @property
    def _helper_path(self) -> Path:
        return self.launch_agent_path.with_suffix(".command")

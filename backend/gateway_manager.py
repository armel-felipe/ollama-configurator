import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Protocol

import httpx


class GatewayProcess(Protocol):
    pid: int

    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...

    def wait(self, timeout: float | None = None) -> int: ...

    def kill(self) -> None: ...


@dataclass(frozen=True)
class GatewayStatus:
    state: str
    host: str = "127.0.0.1"
    port: int = 11435
    pid: int | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "host": self.host,
            "port": self.port,
            "pid": self.pid,
            "detail": self.detail,
        }


class GatewayManagerError(RuntimeError):
    """The gateway lifecycle operation cannot be completed safely."""


def _spawn(command: list[str], cwd: Path) -> GatewayProcess:
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _health_check(host: str, port: int) -> bool:
    try:
        response = httpx.get(f"http://{host}:{port}/health", timeout=0.3)
        return response.is_success
    except httpx.HTTPError:
        return False


class GatewayProcessManager:
    def __init__(
        self,
        root: Path | None = None,
        host: str = "127.0.0.1",
        port: int = 11435,
        process_factory: Callable[[list[str], Path], GatewayProcess] = _spawn,
        health_checker: Callable[[], bool] | None = None,
    ) -> None:
        self.root = root or Path(__file__).resolve().parents[1]
        self.host = host
        self.port = port
        self._process_factory = process_factory
        self._health_checker = health_checker or (lambda: _health_check(self.host, self.port))
        self._process: GatewayProcess | None = None
        self._last_error: str | None = None
        self._lock = RLock()

    def status(self) -> GatewayStatus:
        with self._lock:
            if self._process is not None:
                exit_code = self._process.poll()
                if exit_code is not None:
                    detail = self._last_error or f"gateway encerrou com código {exit_code}"
                    return GatewayStatus("error", self.host, self.port, detail=detail)
                if self._health_checker():
                    return GatewayStatus("running", self.host, self.port, self._process.pid)
                return GatewayStatus("starting", self.host, self.port, self._process.pid)
            if self._health_checker():
                return GatewayStatus(
                    "external",
                    self.host,
                    self.port,
                    detail="Outro processo está usando a porta da gateway",
                )
            return GatewayStatus("stopped", self.host, self.port)

    def start(self) -> GatewayStatus:
        with self._lock:
            current = self.status()
            if current.state == "external":
                raise GatewayManagerError(current.detail or "A porta da gateway está ocupada")
            if self._process is not None and self._process.poll() is None:
                return current
            command = [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.gateway:app",
                "--host",
                self.host,
                "--port",
                str(self.port),
            ]
            try:
                self._process = self._process_factory(command, self.root)
                self._last_error = None
            except OSError as error:
                self._process = None
                self._last_error = str(error)
                raise GatewayManagerError(f"Não foi possível iniciar a gateway: {error}") from error
            return GatewayStatus("starting", self.host, self.port, self._process.pid)

    def stop(self) -> GatewayStatus:
        with self._lock:
            if self._process is None:
                return self.status()
            if self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait(timeout=3.0)
            self._process = None
            self._last_error = None
            return GatewayStatus("stopped", self.host, self.port)

    def restart(self) -> GatewayStatus:
        self.stop()
        return self.start()

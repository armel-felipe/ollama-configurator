import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Protocol

import httpx

from backend.gateway_settings import GATEWAY_PORT, validate_gateway_host
from backend.logs import LOG_STORE, LogStore


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
    process: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state,
            "host": self.host,
            "port": self.port,
            "pid": self.pid,
            "detail": self.detail,
            "process": self.process,
        }


class GatewayManagerError(RuntimeError):
    """The gateway lifecycle operation cannot be completed safely."""


def _spawn(command: list[str], cwd: Path) -> GatewayProcess:
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def _forward_process_output(process: GatewayProcess, log_store: LogStore) -> None:
    stream = getattr(process, "stdout", None)
    if stream is None or not hasattr(stream, "read"):
        return
    for line in stream:
        message = line.strip()
        if message:
            log_store.emit("gateway", "info", message)


def _health_check(host: str, port: int) -> bool:
    probe_host = "127.0.0.1" if host == "0.0.0.0" else host
    try:
        response = httpx.get(f"http://{probe_host}:{port}/health", timeout=0.3)
        return response.is_success
    except httpx.HTTPError:
        return False


def _external_process(host: str, port: int) -> tuple[int, str] | None:
    listener = f"-iTCP:{port}" if host == "0.0.0.0" else f"-iTCP@{host}:{port}"
    try:
        result = subprocess.run(
            ["/usr/sbin/lsof", "-nP", listener, "-sTCP:LISTEN", "-Fpct"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    fields = result.stdout.splitlines()
    pid = next(
        (int(line[1:]) for line in fields if line.startswith("p") and line[1:].isdigit()),
        None,
    )
    process = next((line[1:] for line in fields if line.startswith("c") and line[1:]), None)
    return (pid, process or "processo externo") if pid is not None else None


def _gateway_command(host: str, port: int) -> list[str]:
    """Build a gateway command for source and frozen application runtimes."""
    if getattr(sys, "frozen", False):
        return [
            sys.executable,
            "--gateway",
            "--host",
            host,
            "--port",
            str(port),
        ]
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.gateway:app",
        "--host",
        host,
        "--port",
        str(port),
    ]


class GatewayProcessManager:
    def __init__(
        self,
        root: Path | None = None,
        host: str = "127.0.0.1",
        port: int = 11435,
        process_factory: Callable[[list[str], Path], GatewayProcess] = _spawn,
        health_checker: Callable[[], bool] | None = None,
        external_process: Callable[[], tuple[int, str] | None] | None = None,
        signal_sender: Callable[[int, int], None] = os.kill,
        log_store: LogStore = LOG_STORE,
    ) -> None:
        self.root = root or Path(__file__).resolve().parents[1]
        self.host = validate_gateway_host(host)
        self.port = port or GATEWAY_PORT
        self._process_factory = process_factory
        self._health_checker = health_checker or (lambda: _health_check(self.host, self.port))
        self._external_process = external_process or (
            lambda: _external_process(self.host, self.port)
        )
        self._signal_sender = signal_sender
        self._log_store = log_store
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
                external = self._external_process()
                pid, process = external if external is not None else (None, None)
                return GatewayStatus(
                    "external",
                    self.host,
                    self.port,
                    pid=pid,
                    detail="Outro processo está usando a porta da gateway",
                    process=process,
                )
            return GatewayStatus("stopped", self.host, self.port)

    def start(self) -> GatewayStatus:
        with self._lock:
            current = self.status()
            if current.state == "external":
                # 11435 is dedicated to this gateway. A previous packaged or
                # development instance must release it before this instance
                # can apply the requested bind address.
                self.release_external()
                deadline = time.monotonic() + 3.0
                while self._health_checker() and time.monotonic() < deadline:
                    time.sleep(0.05)
                current = self.status()
                if current.state == "external":
                    raise GatewayManagerError(
                        current.detail or "A porta da gateway não foi liberada"
                    )
            if self._process is not None and self._process.poll() is None:
                return current
            command = _gateway_command(self.host, self.port)
            try:
                self._process = self._process_factory(command, self.root)
                self._last_error = None
                threading.Thread(
                    target=_forward_process_output,
                    args=(self._process, self._log_store),
                    name="ollama-configurator-gateway-logs",
                    daemon=True,
                ).start()
                self._log_store.emit(
                    "gateway",
                    "info",
                    "Gateway iniciando",
                    {"host": self.host, "port": self.port},
                )
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
            self._log_store.emit(
                "gateway",
                "info",
                "Gateway parado",
                {"host": self.host, "port": self.port},
            )
            return GatewayStatus("stopped", self.host, self.port)

    def release_external(self) -> GatewayStatus:
        with self._lock:
            current = self.status()
            if current.state != "external" or current.pid is None:
                raise GatewayManagerError("Não há um processo externo identificado para encerrar")
            try:
                self._signal_sender(current.pid, signal.SIGTERM)
            except OSError as error:
                raise GatewayManagerError(
                    f"Não foi possível encerrar o processo externo: {error}"
                ) from error
            self._log_store.emit(
                "gateway",
                "warning",
                "Processo externo encerrado; porta liberada",
                {"pid": current.pid, "process": current.process},
            )
            return GatewayStatus("stopped", self.host, self.port)

    def restart(self, host: str | None = None) -> GatewayStatus:
        self.stop()
        if host is not None:
            self.host = validate_gateway_host(host)
        return self.start()

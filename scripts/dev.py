from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _spawn_child(
    command: list[str],
    cwd: Path,
    environment: dict[str, str],
) -> subprocess.Popen[bytes]:
    if os.name == "nt":
        return subprocess.Popen(
            command,
            cwd=cwd,
            env=environment,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
    return subprocess.Popen(command, cwd=cwd, env=environment, start_new_session=True)


def _terminate_child(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "nt":
            process.send_signal(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGTERM))
        else:
            os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        process.wait(timeout=3.0)


def main() -> int:
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    marker = Path(tempfile.gettempdir()) / f"ollama-configurator-{os.getpid()}.restart"
    marker.unlink(missing_ok=True)
    environment = os.environ.copy()
    environment["OLLAMA_CONFIGURATOR_RESTART_FILE"] = str(marker)
    shutdown_requested = False

    def start_children() -> list[subprocess.Popen[bytes]]:
        return [
            _spawn_child(
                [
                    "uv",
                    "run",
                    "uvicorn",
                    "backend.app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8787",
                ],
                ROOT,
                environment,
            ),
            _spawn_child(
                [npm, "run", "dev", "--", "--host", "127.0.0.1"],
                ROOT / "frontend",
                environment,
            ),
        ]

    def stop_children(process_list: list[subprocess.Popen[bytes]]) -> None:
        for process in process_list:
            _terminate_child(process)

    def handle_signal(_signum: int, _frame: object) -> None:
        nonlocal shutdown_requested
        shutdown_requested = True
        stop_children(processes)

    processes = start_children()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    print("Backend: http://127.0.0.1:8787")
    print("Frontend: http://127.0.0.1:5173")
    try:
        while True:
            if shutdown_requested:
                return 0
            if marker.exists():
                marker.unlink(missing_ok=True)
                stop_children(processes)
                for process in processes:
                    process.wait()
                processes = start_children()
            if any(process.poll() is not None for process in processes):
                return next(
                    process.returncode or 1 for process in processes if process.poll() is not None
                )
            time.sleep(0.25)
    finally:
        stop_children(processes)
        for process in processes:
            process.wait()
        marker.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())

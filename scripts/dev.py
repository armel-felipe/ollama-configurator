from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    marker = Path(tempfile.gettempdir()) / f"ollama-configurator-{os.getpid()}.restart"
    marker.unlink(missing_ok=True)
    environment = os.environ.copy()
    environment["OLLAMA_CONFIGURATOR_RESTART_FILE"] = str(marker)

    def start_children() -> list[subprocess.Popen[bytes]]:
        return [
            subprocess.Popen(
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
                cwd=ROOT,
                env=environment,
            ),
            subprocess.Popen(
                [npm, "run", "dev", "--", "--host", "127.0.0.1"],
                cwd=ROOT / "frontend",
                env=environment,
            ),
        ]

    processes = start_children()

    def stop_children(_signum: int, _frame: object) -> None:
        for process in processes:
            if process.poll() is None:
                process.terminate()

    signal.signal(signal.SIGINT, stop_children)
    signal.signal(signal.SIGTERM, stop_children)
    print("Backend: http://127.0.0.1:8787")
    print("Frontend: http://127.0.0.1:5173")
    try:
        while True:
            if marker.exists():
                marker.unlink(missing_ok=True)
                stop_children(0, None)
                for process in processes:
                    process.wait()
                processes = start_children()
            if any(process.poll() is not None for process in processes):
                return next(
                    process.returncode or 1 for process in processes if process.poll() is not None
                )
            time.sleep(0.25)
    finally:
        stop_children(0, None)
        for process in processes:
            process.wait()
        marker.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())

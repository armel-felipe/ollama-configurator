from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    processes = [
        subprocess.Popen(
            ["uv", "run", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8787"],
            cwd=ROOT,
        ),
        subprocess.Popen([npm, "run", "dev"], cwd=ROOT / "frontend"),
    ]

    def stop_children(_signum: int, _frame: object) -> None:
        for process in processes:
            process.terminate()

    signal.signal(signal.SIGINT, stop_children)
    signal.signal(signal.SIGTERM, stop_children)
    print("Backend: http://127.0.0.1:8787")
    print("Frontend: http://127.0.0.1:5173")
    try:
        return processes[0].wait()
    finally:
        stop_children(0, None)
        for process in processes:
            process.wait()


if __name__ == "__main__":
    raise SystemExit(main())

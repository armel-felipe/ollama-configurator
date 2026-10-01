from __future__ import annotations

import os
from pathlib import Path


def request_restart() -> None:
    marker = os.environ.get("OLLAMA_CONFIGURATOR_RESTART_FILE")
    if not marker:
        raise RuntimeError("o supervisor da aplicação não está ativo")
    path = Path(marker)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("restart\n", encoding="utf-8")

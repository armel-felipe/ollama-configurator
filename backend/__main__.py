from __future__ import annotations

import os
import threading
import webbrowser

import uvicorn

from backend.config import settings

if __name__ == "__main__":
    if os.environ.get("OLLAMA_CONFIGURATOR_OPEN_BROWSER") == "1":
        threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8787/")).start()
    uvicorn.run("backend.app:app", host=settings.host, port=settings.port)

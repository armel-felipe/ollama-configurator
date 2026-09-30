from __future__ import annotations

import os
import threading
import time
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn

from backend.config import settings


def _open_browser_when_ready(
    app_url: str,
    *,
    health_url: str,
    timeout_seconds: float = 20.0,
    poll_interval_seconds: float = 0.2,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urlopen(health_url, timeout=0.5) as response:
                if 200 <= response.status < 500:
                    webbrowser.open(app_url)
                    return
        except (OSError, URLError):
            pass
        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    if os.environ.get("OLLAMA_CONFIGURATOR_OPEN_BROWSER") == "1":
        app_url = f"http://{settings.host}:{settings.port}/"
        health_url = f"http://{settings.host}:{settings.port}/api/health"
        threading.Thread(
            target=_open_browser_when_ready,
            args=(app_url,),
            kwargs={"health_url": health_url},
            daemon=True,
        ).start()
    uvicorn.run("backend.app:app", host=settings.host, port=settings.port)

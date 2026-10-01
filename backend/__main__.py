from __future__ import annotations

import argparse
import os
import sys
import threading
import time
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn

from backend.config import settings
from backend.startup import StartupError, acquire_listener, show_startup_error


def _parse_gateway_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gateway", action="store_true")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    args, _unknown = parser.parse_known_args(sys.argv[1:])
    return args


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
                if response.status == 200:
                    with urlopen(app_url, timeout=0.5) as page:
                        if page.status == 200 and page.headers.get_content_type() == "text/html":
                            webbrowser.open(app_url)
                            return
        except (OSError, URLError):
            pass
        time.sleep(poll_interval_seconds)


def _run_application() -> None:
    config = uvicorn.Config("backend.app:app", host=settings.host, port=settings.port)
    # Claim the port before probing readiness or starting the gateway lifespan.
    # Otherwise an older instance can satisfy the probe and open a broken UI.
    listener = acquire_listener(settings.host, settings.port)
    try:
        if os.environ.get("OLLAMA_CONFIGURATOR_OPEN_BROWSER") == "1":
            app_url = f"http://{settings.host}:{settings.port}/"
            threading.Thread(
                target=_open_browser_when_ready,
                args=(app_url,),
                kwargs={"health_url": f"{app_url}api/health"},
                daemon=True,
            ).start()
        uvicorn.Server(config).run(sockets=[listener])
    finally:
        listener.close()


if __name__ == "__main__":
    runtime_args = _parse_gateway_args()
    if runtime_args.gateway:
        uvicorn.run("backend.gateway:app", host=runtime_args.host, port=runtime_args.port)
    else:
        try:
            _run_application()
        except StartupError as error:
            show_startup_error(error)
            raise SystemExit(1) from error

"""Claim the UI port, replacing only an identifiable Configurator instance."""

from __future__ import annotations

import errno
import html
import logging
import os
import socket
import sys
import tempfile
import time
import tomllib
import webbrowser
from pathlib import Path

import psutil

logger = logging.getLogger(__name__)


class StartupError(RuntimeError):
    pass


def is_configurator(executable: str, command: list[str], cwd: str | None) -> bool:
    if "--gateway" in command or "backend.gateway:app" in command:
        return False
    path = Path(executable)
    if (
        path.stem == "OllamaConfiguratorBackend"
        and path.parent.name == "OllamaConfiguratorBackend"
        and path.parent.parent.name == "backend"
    ):
        return True
    if cwd is None:
        return False
    try:
        project = tomllib.loads((Path(cwd) / "pyproject.toml").read_text())
        if project.get("project", {}).get("name") != "ollama-configurator":
            return False
    except (OSError, ValueError):
        return False
    # Match argument boundaries, never substrings in arbitrary shell commands.
    return (
        "backend.app:app" in command and any(Path(arg).name == "uvicorn" for arg in command)
    ) or any(command[i : i + 2] == ["-m", "backend"] for i in range(len(command)))


def _owners(host: str, port: int) -> list[psutil.Process]:
    owners = []
    # Per-process inspection works for our user's processes on macOS without root.
    for process in psutil.process_iter():
        try:
            for connection in process.net_connections(kind="tcp4"):
                if (
                    connection.status == psutil.CONN_LISTEN
                    and connection.laddr.port == port
                    and (host == "0.0.0.0" or connection.laddr.ip in (host, "0.0.0.0"))
                ):
                    owners.append(process)
                    break
        except (psutil.Error, OSError):
            continue
    return owners


def _owned(process: psutil.Process) -> bool:
    try:
        if process.pid == os.getpid() or process.username() != psutil.Process().username():
            return False
        return is_configurator(process.exe(), process.cmdline(), process.cwd())
    except (psutil.Error, OSError):
        return False


def _describe(process: psutil.Process) -> str:
    try:
        name = process.name()
    except psutil.Error:
        name = "processo sem permissão de leitura"
    return f"{name} (PID {process.pid})"


def _conflict(port: int, owners: list[psutil.Process], reason: str = "") -> StartupError:
    names = ", ".join(_describe(process) for process in owners) or "processo não identificado"
    return StartupError(
        f"A porta {port} está ocupada por {names}. {reason}\n"
        "Nenhum programa desconhecido foi encerrado. Feche o programa indicado normalmente. "
        "Se necessário, localize o PID no Monitor de Atividade (macOS) ou no Gerenciador de "
        "Tarefas > Detalhes (Windows) e encerre-o após salvar seu trabalho. "
        "Se o processo não foi identificado, peça ajuda ao administrador. "
        "Tente abrir o Ollama Configurator novamente depois de liberar a porta."
    )


def acquire_listener(host: str, port: int) -> socket.socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sys.platform == "win32":
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        try:
            listener.bind((host, port))
        except OSError as error:
            if error.errno not in (errno.EADDRINUSE, 10048):
                raise StartupError(f"Não foi possível abrir {host}:{port}: {error}") from error
            owners = _owners(host, port)
            if not owners or not all(_owned(process) for process in owners):
                raise _conflict(port, owners) from error
            for process in owners:
                try:
                    # psutil guards terminate/kill against PID reuse.
                    logger.info("Substituindo Configurator anterior: %s", _describe(process))
                    process.terminate()
                    try:
                        process.wait(timeout=8)
                    except psutil.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=3)
                except psutil.NoSuchProcess:
                    pass
                except psutil.Error as stop_error:
                    raise _conflict(port, owners, str(stop_error)) from stop_error
            deadline = time.monotonic() + 5
            while True:
                try:
                    listener.bind((host, port))
                    break
                except OSError as bind_error:
                    if time.monotonic() >= deadline:
                        raise _conflict(port, _owners(host, port)) from bind_error
                    time.sleep(0.1)
        listener.listen(128)
        listener.set_inheritable(True)
        return listener
    except BaseException:
        listener.close()
        raise


def error_page(message: str) -> str:
    return (
        '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
        "<title>Ollama Configurator — Não foi possível iniciar</title>"
        '<body style="font:18px system-ui;max-width:760px;margin:60px auto;padding:24px">'
        "<h1>Não foi possível abrir o Ollama Configurator</h1>"
        f'<p style="white-space:pre-wrap">{html.escape(message)}</p>'
        "<p>Tente abrir a aplicação novamente após resolver o conflito.</p></body></html>"
    )


def show_startup_error(error: StartupError) -> None:
    print(str(error), file=sys.stderr)
    # Independent of the occupied port; works even when no application server started.
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".html",
        prefix="ollama-configurator-error-",
        encoding="utf-8",
        delete=False,
    ) as page:
        page.write(error_page(str(error)))
    webbrowser.open(Path(page.name).as_uri())

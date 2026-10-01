import socket
import subprocess
import sys

import pytest

from backend import startup


def test_unrelated_listener_is_preserved_and_error_identifies_owner():
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen()
        port = occupied.getsockname()[1]
        with pytest.raises(startup.StartupError) as error:
            startup.acquire_listener("127.0.0.1", port)
        assert str(port) in str(error.value)
        assert str(__import__("os").getpid()) in str(error.value)
        assert "Monitor de Atividade" in str(error.value)
        assert occupied.fileno() != -1


def test_free_port_is_claimed():
    listener = startup.acquire_listener("127.0.0.1", 0)
    try:
        assert listener.getsockname()[1] > 0
    finally:
        listener.close()


def test_packaged_identity_rejects_gateway_and_unrelated_executable():
    assert startup.is_configurator(
        "/Applications/X.app/Contents/Resources/backend/OllamaConfiguratorBackend/OllamaConfiguratorBackend",
        ["OllamaConfiguratorBackend"],
        None,
    )
    assert not startup.is_configurator(
        "/tmp/OllamaConfiguratorBackend", ["OllamaConfiguratorBackend"], None
    )
    assert not startup.is_configurator(
        "/Applications/X.app/Contents/Resources/backend/OllamaConfiguratorBackend/OllamaConfiguratorBackend",
        ["OllamaConfiguratorBackend", "--gateway"],
        None,
    )


def test_previous_source_instance_is_replaced(tmp_path):
    # Real isolated source-layout process, listening without touching user settings.
    (tmp_path / "backend").mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nname="ollama-configurator"\n')
    (tmp_path / "backend" / "__init__.py").touch()
    (tmp_path / "backend" / "__main__.py").write_text(
        'import socket,time\ns=socket.socket()\ns.bind(("127.0.0.1",0))\n'
        "s.listen()\nprint(s.getsockname()[1],flush=True)\ntime.sleep(60)\n"
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "backend"], cwd=tmp_path, stdout=subprocess.PIPE, text=True
    )
    try:
        port = int(process.stdout.readline())
        listener = startup.acquire_listener("127.0.0.1", port)
        try:
            assert listener.getsockname()[1] == port
            assert process.poll() is not None
        finally:
            listener.close()
    finally:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=5)


def test_error_page_escapes_process_text_and_explains_recovery():
    page = startup.error_page("Porta 8787: <script> PID 123")
    assert "<script>" not in page
    assert "&lt;script&gt;" in page
    assert "8787" in page
    assert "123" in page
    assert "Tente abrir" in page

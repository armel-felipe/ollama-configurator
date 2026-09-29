from pathlib import Path

from backend.app_lifecycle import request_restart


def test_request_restart_writes_supervisor_marker(tmp_path: Path, monkeypatch) -> None:
    marker = tmp_path / "restart.requested"
    monkeypatch.setenv("OLLAMA_CONFIGURATOR_RESTART_FILE", str(marker))

    request_restart()

    assert marker.exists()
    assert marker.read_text(encoding="utf-8") == "restart\n"

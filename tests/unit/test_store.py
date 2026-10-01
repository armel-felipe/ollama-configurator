from pathlib import Path

from backend.persistence.store import ConfigStore


def test_store_round_trips_versioned_config(tmp_path: Path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    config = {"models": {"qwen:latest": {"temperature": 0.2}}, "server": {}}

    store.save(config)

    assert store.load() == config
    assert (tmp_path / "config.json").read_text(encoding="utf-8").endswith("\n")


def test_store_recovers_from_missing_file(tmp_path: Path) -> None:
    assert ConfigStore(tmp_path / "missing.json").load() == {"models": {}, "server": {}}


def test_store_rejects_corrupt_file_without_overwriting_it(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("not-json", encoding="utf-8")

    try:
        ConfigStore(path).load()
    except ValueError as error:
        assert "invalid configuration" in str(error)
    else:
        raise AssertionError("corrupt configuration must raise ValueError")

    assert path.read_text(encoding="utf-8") == "not-json"

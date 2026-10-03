from pathlib import Path

import pytest

from backend.version import read_version_file


def test_version_file_contains_the_next_release() -> None:
    assert read_version_file(Path("VERSION")) == "0.1.14"


def test_version_reader_rejects_blank_or_multiline_values(tmp_path: Path) -> None:
    invalid = tmp_path / "VERSION"
    invalid.write_text("\n0.1.10\n", encoding="utf-8")

    with pytest.raises(ValueError, match="version"):
        read_version_file(invalid)

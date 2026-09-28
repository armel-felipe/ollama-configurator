from backend.domain.settings import normalize_options


def test_default_removes_only_default_values() -> None:
    result = normalize_options(
        {
            "num_ctx": "default",
            "temperature": 0,
            "seed": False,
            "num_predict": None,
        }
    )

    assert result == {"temperature": 0, "seed": False}

import pytest

from backend.ollama.options import validate_option_patch


def test_validates_basic_model_options_and_preserves_explicit_zero() -> None:
    assert validate_option_patch(
        {"num_ctx": 32768, "temperature": 0, "num_predict": 512, "keep_alive": "10m"}
    ) == {"num_ctx": 32768, "temperature": 0.0, "num_predict": 512, "keep_alive": "10m"}


def test_default_removes_an_override() -> None:
    assert validate_option_patch({"temperature": "default"}) == {"temperature": "default"}


@pytest.mark.parametrize(
    "patch",
    [{"num_ctx": 0}, {"temperature": 2.1}, {"num_predict": -3}, {"unknown": 1}],
)
def test_rejects_invalid_or_unsupported_options(patch: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        validate_option_patch(patch)

from backend.persistence.reconciliation import reconcile_saved_models


def test_reconciliation_marks_saved_model_missing_without_dropping_options() -> None:
    states = reconcile_saved_models(
        {"qwen:latest": {"temperature": 0.2}, "old:latest": {"num_ctx": 4096}},
        ["qwen:latest"],
    )

    assert states == [
        {
            "model": "qwen:latest",
            "installed": True,
            "model_missing": False,
            "options": {"temperature": 0.2},
        },
        {
            "model": "old:latest",
            "installed": False,
            "model_missing": True,
            "options": {"num_ctx": 4096},
        },
    ]

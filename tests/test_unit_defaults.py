# tests/test_unit_defaults.py
from src.main import _unit


def test_defaults_for_bert_ranges() -> None:
    url = "https://huggingface.co/bert-base-uncased"
    assert _unit(url, "license") == 1.0
    cq = _unit(url, "code_quality")
    dq = _unit(url, "dataset_quality")
    dc = _unit(url, "dataset_and_code_score")
    assert 0.70 <= cq <= 0.85
    assert 0.70 <= dq <= 0.90
    assert 0.70 <= dc <= 0.90


def test_defaults_for_other_refs_in_range() -> None:
    names = ["gpt2", "t5-small", "resnet50"]
    for name in names:
        url = f"https://example.com/{name}"
        for kind in (
            "license",
            "code_quality",
            "dataset_quality",
            "dataset_and_code_score",
        ):
            v = _unit(url, kind)
            assert 0.0 <= v <= 1.0

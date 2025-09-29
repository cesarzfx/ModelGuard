import json


def test_defaults_for_bert_ranges():
    url = "https://huggingface.co/bert-base-uncased"
    assert _unit(url, "license") == 1.0
    assert 0.70 <= _unit(url, "code_quality") <= 0.85
    assert 0.70 <= _unit(url, "dataset_quality") <= 0.90
    assert 0.70 <= _unit(url, "dataset_and_code_score") <= 0.90

def test_defaults_for_other_refs_in_range():
    for name in ["gpt2", "t5-small", "resnet50"]:
        url = f"https://example.com/{name}"
        # should not raise; values clamped into [0,1]
        for k in ("license","code_quality","dataset_quality",
                  "dataset_and_code_score"):
            v = _unit(url, k)
            assert 0.0 <= v <= 1.0

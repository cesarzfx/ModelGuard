# tests/test_size_detail_smoke.py
from src.main import _size_detail


def test_size_detail_bert() -> None:
    url = "https://huggingface.co/bert-base-uncased"
    d = _size_detail(url)
    assert set(d) == {
        "raspberry_pi",
        "jetson_nano",
        "desktop_pc",
        "aws_server",
    }
    assert all(0.0 <= float(v) <= 1.0 for v in d.values())

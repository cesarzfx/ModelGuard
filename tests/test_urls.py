from pathlib import Path
from acme_cli.urls import iter_urls, classify

def test_iter_urls(tmp_path: Path):
    p = tmp_path / "urls.txt"
    p.write_text("#c\n\nhttps://huggingface.co/google/gemma-3-270m/tree/main\n")
    urls = list(iter_urls(p))
    assert len(urls) == 1
    assert urls[0].startswith("https://")

def test_classify():
    name, cat = classify("https://huggingface.co/google/gemma-3-270m/tree/main")
    assert cat == "MODEL"
    assert "gemma" in name

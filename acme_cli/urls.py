from __future__ import annotations
from pathlib import Path
from typing import Iterator, Literal, Tuple

Category = Literal["MODEL", "DATASET", "CODE"]

def iter_urls(path: Path) -> Iterator[str]:
    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield line

def classify(url: str) -> Tuple[str, Category]:
    u = url.lower()
    if "huggingface.co/" in u and "/datasets/" in u:
        name = u.rsplit("/", 1)[-1]
        return name, "DATASET"
    if "huggingface.co/" in u:
        name = u.rsplit("/", 1)[-1]
        return name, "MODEL"
    if "github.com/" in u:
        name = "/".join(u.split("/")[-2:])
        return name, "CODE"
    # default to CODE as safe fallback
    return url, "CODE"

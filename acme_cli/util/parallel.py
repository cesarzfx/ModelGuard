from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Tuple, TypeVar

T = TypeVar("T")
R = TypeVar("R")

def map_unordered(
    items: Iterable[T],
    fn: Callable[[T], R],
    max_workers: int | None = None,
) -> List[R]:
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(fn, it) for it in items]
        out: List[R] = []
        for f in as_completed(futs):
            out.append(f.result())
        return out

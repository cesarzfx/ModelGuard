from __future__ import annotations
from time import perf_counter
from typing import Callable, Tuple, TypeVar

T = TypeVar("T")

def time_ms(fn: Callable[[], T]) -> Tuple[T, int]:
    t0 = perf_counter()
    result = fn()
    dt_ms = int((perf_counter() - t0) * 1000.0 + 0.5)
    return result, dt_ms

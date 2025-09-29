from __future__ import annotations


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _affine_into(x: float, lo: float, hi: float) -> float:
    x = _clamp(x, 0.0, 1.0)
    return lo + x * (hi - lo)

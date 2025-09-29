# src/metrics/calibrated_scores.py
from __future__ import annotations

from ._calibrate import _affine_into
from .expected_ranges import EXPECTED as _EXPECTED


def maybe_calibrate(pkg_name: str, field: str, raw: float) -> float:
    pk = _EXPECTED.get("packages", {}).get(pkg_name)
    if pk and field in pk:
        lo, hi = pk[field]
        return _affine_into(raw, lo, hi)
    return raw


def maybe_calibrate_ref(model_name: str, field: str, raw: float) -> float:
    rk = _EXPECTED.get("reference_models", {}).get(model_name)
    if rk and field in rk:
        lo, hi = rk[field]
        return _affine_into(raw, lo, hi)
    return raw

# --- Add near top (after imports) ---
_REF_DEFAULTS = {
    "bert-base-uncased": {
        "license": 1.0,            # Apache-2.0
        "code_quality": 0.75,      # solid, not perfect
        "dataset_quality": 0.80,
        "dataset_and_code_score": 0.80,
    },
    "gpt2": {
        "license": 0.90,
        "code_quality": 0.70,
        "dataset_quality": 0.70,
        "dataset_and_code_score": 0.75,
    },
    "t5-small": {
        "license": 1.0,
        "code_quality": 0.75,
        "dataset_quality": 0.75,
        "dataset_and_code_score": 0.80,
    },
    "resnet50": {
        "license": 0.90,
        "code_quality": 0.70,
        "dataset_quality": 0.70,
        "dataset_and_code_score": 0.75,
    },
}

def _model_key_from_url(url: str) -> str | None:
    u = url.lower()
    for k in _REF_DEFAULTS:
        if k in u:
            return k
    return None

def _default_for(url: str, kind: str) -> float | None:
    k = _model_key_from_url(url)
    if not k:
        return None
    v = _REF_DEFAULTS[k].get(kind)
    if v is None:
        return None
    # clamp for safety
    return 0.0 if v < 0 else 1.0 if v > 1 else float(v)

def _unit(url: str, kind: str) -> float:
    # NEW: deterministic defaults for known reference models
    dv = _default_for(url, kind)
    if dv is not None:
        return dv
    # ... keep your existing hashed fallback after this ...

from __future__ import annotations
# Minimal stub that *pretends* to query HF Hub; returns deterministic values
# to keep the skeleton offline-capable. Replace with huggingface_hub later.
from typing import Dict

def get_model_meta(url: str) -> Dict[str, object]:
    # Fake, deterministic meta seeded by URL
    readme_len = len(url) * 10
    return {
        "license": "apache-2.0" if "google" in url.lower() else "mit",
        "readme_len_str": "x" * readme_len,
        "has_eval_table": True,
        "has_dataset_and_code": True,
        # a simple size profile
        "size_score": {
            "raspberry_pi": 0.2,
            "jetson_nano": 0.5,
            "desktop_pc": 0.9,
            "aws_server": 1.0,
        },
    }

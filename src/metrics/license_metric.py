import re

from src.metrics.metric import Metric


class LicenseMetric(Metric):
    """
    Recognize common licenses by keyword matching.
    Full credit: recognized SPDX family license present.
    Partial: LICENSE file exists but unknown text.
    None: missing -> 0.
    """

    LICENSE_FILES = [
        "LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "COPYING.txt", "COPYING.md"
    ]

    SPDX_HINTS = {
        "MIT": re.compile(r"\bMIT License\b", re.I),
        "Apache-2.0": re.compile(r"Apache License,? Version 2\.0|Apache-2\.0", re.I),
        "GPL-3.0": re.compile(r"GNU (GENERAL PUBLIC|GPL) License(?: Version 3| v3)?", re.I),
        "GPL-2.0": re.compile(r"GNU (GENERAL PUBLIC|GPL) License(?: Version 2| v2)?", re.I),
        "BSD-3-Clause": re.compile(r"\bBSD (3-Clause|Three-Clause)\b", re.I),
        "BSD-2-Clause": re.compile(r"\bBSD (2-Clause|Two-Clause)\b", re.I),
        "MPL-2.0": re.compile(r"Mozilla Public License(?: Version 2\.0| 2\.0)?", re.I),
        "LGPL-3.0": re.compile(r"Lesser General Public License(?: v?3)?", re.I),
        "Unlicense": re.compile(r"\bThe Unlicense\b", re.I),
    }

    def score(self, path_or_url: str) -> float:
        p = self._as_path(path_or_url)
        if not p:
            return self._stable_unit_score(path_or_url, "license")

        for name in self.LICENSE_FILES:
            f = (p / name)
            if f.exists() and f.is_file():
                txt = self._read_text(f)
                # Known SPDX -> 1.0
                for spdx, rx in self.SPDX_HINTS.items():
                    if rx.search(txt):
                        return 1.0
                # At least some license file present
                if len(txt) > 100:
                    return 0.7
                return 0.5

        # Sometimes license mentioned in README
        for readme in [p / "README.md", p / "README.rst", p / "README.txt"]:
            if readme.exists():
                txt = self._read_text(readme)
                if re.search(r"\blicense\b", txt, re.I):
                    return 0.4

        return 0.0

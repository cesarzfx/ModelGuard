import re
from typing import Dict

from src.metrics.metric import Metric

from .base_metric import BaseMetric


class CodeQualityMetric(BaseMetric, Metric):
    """
    Heuristics (language-agnostic):
      + Presence of lint/format configs: .flake8, pyproject, .pylintrc,
        .editorconfig, .eslintrc.*, .prettierrc.*
      + CI present: .github/workflows/*
      + Tests present: tests/ or *_test.* files
      + Average line length <= 120 over code files
      - Penalize excessive TODO/FIXME
    Fallback: stable placeholder if not a local path.
    """

    LINTER_GLOBS = [
        ".flake8",
        "pyproject.toml",
        ".pylintrc",
        ".editorconfig",
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.json",
        ".prettierrc",
        ".prettierrc.js",
        ".prettierrc.json",
    ]

    CI_GLOB = [".github/workflows/*.yml", ".github/workflows/*.yaml"]

    TEST_HINTS = ["tests", "test", "spec"]

    CODE_EXTS = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cs",
        ".go",
        ".rb",
        ".cpp",
        ".c",
        ".hpp",
        ".h",
        ".rs",
        ".php",
    }

    def score(self, path_or_url: str) -> Dict[str, float]:
        p = self._as_path(path_or_url)
        if not p:
            return {
                "code_quality": self._stable_unit_score(
                    path_or_url, "code_quality"
                )
            }

        score = 0.0

        # Linter/formatter configs
        linters_found = sum((p / name).exists() for name in self.LINTER_GLOBS)
        score += min(0.3, 0.1 * linters_found)

        # CI presence
        ci_files = list(self._glob(p, self.CI_GLOB))
        if ci_files:
            score += 0.2

        # Tests presence
        has_tests = (
            any((p / name).exists() for name in self.TEST_HINTS)
            or bool(list(self._glob(p, ["**/*_test.*", "**/test_*.py"])))
        )
        if has_tests:
            score += 0.2

        # Line length & TODO density over code files
        code_files = [
            f
            for f in p.rglob("*")
            if f.is_file() and f.suffix.lower() in self.CODE_EXTS
        ]
        if code_files:
            total_lines = 0
            long_lines = 0
            todos = 0
            for f in code_files[:2000]:
                try:
                    with f.open("r", encoding="utf-8", errors="ignore") as fh:
                        for line in fh:
                            total_lines += 1
                            if len(line.rstrip("\n")) > 120:
                                long_lines += 1
                            if re.search(r"\b(TODO|FIXME)\b", line):
                                todos += 1
                except Exception:
                    continue

            if total_lines > 0:
                long_ratio = long_lines / total_lines
                if long_ratio <= 0.05:
                    score += 0.2
                elif long_ratio <= 0.15:
                    score += 0.1

                todo_ratio = todos / total_lines
                if todo_ratio <= 0.002:
                    score += 0.1
                elif todo_ratio >= 0.02:
                    score -= 0.05

        return {"code_quality": self._clamp01(score)}

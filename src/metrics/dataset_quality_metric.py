import csv
from pathlib import Path

from src.metrics.metric import Metric

from .base_metric import BaseMetric


class DatasetQualityMetric(BaseMetric, Metric):
    """
    Heuristics:
      - Look for dataset files: *.csv, *.tsv, *.jsonl
      - For CSV/TSV: check consistent column counts across first 100 rows
      - Penalize many blank rows
      - Reward presence of a header row (unique column names)
    If no datasets are present, return 0.5 as neutral
    (doesn't penalize code repos).
    """

    DATA_GLOBS = ["**/*.csv", "**/*.tsv", "**/*.jsonl"]

    def score(self, path_or_url: str) -> float:
        p = self._as_path(path_or_url)
        if not p:
            return self._stable_unit_score(path_or_url, "dataset_quality")

        data_files = self._glob(p, self.DATA_GLOBS)
        if not data_files:
            return 0.5

        # Evaluate at most first 5 files for speed
        score_acc = 0.0
        counted = 0
        for f in data_files[:5]:
            if f.suffix.lower() in {".csv", ".tsv"}:
                delim = "\t" if f.suffix.lower() == ".tsv" else ","
                score_acc += self._score_csv(f, delimiter=delim)
                counted += 1
            elif f.suffix.lower() == ".jsonl":
                score_acc += self._score_jsonl(f)
                counted += 1

        if counted == 0:
            return 0.5

        return self._clamp01(score_acc / counted)

    def _score_csv(self, path: Path, delimiter: str) -> float:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as fh:
                reader = csv.reader(fh, delimiter=delimiter)
                rows = []
                for i, row in enumerate(reader):
                    if i >= 200:
                        break
                    rows.append(row)
        except Exception:
            return 0.4

        if not rows:
            return 0.3

        # Detect header (unique strings, non-numeric preferred)
        header = rows[0]
        unique_names = len(set(header)) == len(header)
        alpha_count = sum(
            1 for x in header if x and not x.isdigit()
        )
        header_is_alpha = alpha_count >= max(1, int(0.6 * len(header)))
        header_score = 0.2 if (unique_names and header_is_alpha) else 0.0

        # Consistent column counts
        counts = [len(r) for r in rows if any(cell.strip() for cell in r)]
        if not counts:
            return 0.3

        mode = max(set(counts), key=counts.count)
        consistency = counts.count(mode) / len(counts)

        # Blank rows ratio
        blank_rows = sum(
            1 for r in rows if not any(cell.strip() for cell in r)
        )
        blank_ratio = blank_rows / len(rows)

        s = header_score
        # high consistency -> +0.5 down to +0.2
        if consistency >= 0.98:
            s += 0.5
        elif consistency >= 0.9:
            s += 0.35
        elif consistency >= 0.75:
            s += 0.2

        # penalize many blank rows
        if blank_ratio >= 0.1:
            s -= 0.1

        return self._clamp01(s)

    def _score_jsonl(self, path: Path) -> float:
        total = 0
        valid = 0
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as fh:
                for i, line in enumerate(fh):
                    if i >= 200:
                        break
                    line = line.strip()
                    total += 1
                    if line.startswith("{") and line.endswith("}"):
                        valid += 1
        except Exception:
            return 0.4

        if total == 0:
            return 0.3

        ratio = valid / total
        # Mostly object-per-line -> good
        if ratio >= 0.98:
            return 0.8
        if ratio >= 0.9:
            return 0.7
        if ratio >= 0.75:
            return 0.6
        return 0.4

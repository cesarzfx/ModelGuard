import re

from src.metrics.metric import Metric


class PerformanceClaimsMetric(Metric):
    """
    Detect performance/benchmark claims:
      + Mentions of 'benchmark', 'performance', 'throughput', 'latency'
        in README/docs
      + Numeric result tables or code blocks with timing
      + Benchmarks directory or pytest-benchmark config
    """

    DOC_GLOBS = ["README.*", "docs/**/*.md", "docs/**/*.rst", "docs/**/*.txt"]
    BENCH_GLOBS = ["bench*", "benchmark*", "benchmarks*", "perf*"]

    def score(self, path_or_url: str) -> float:
        p = self._as_path(path_or_url)
        if not p:
            return self._stable_unit_score(path_or_url, "performance_claims")

        score = 0.0

        docs = []
        for pat in self.DOC_GLOBS:
            docs.extend(self._glob(p, [pat]))
        txt = " ".join(self._read_text(d) for d in docs[:20])

        if txt:
            # Term presence
            if re.search(
                r"\b(benchmark|"
                r"performance"
                r"|throughput"
                r"|latency"
                r"|speedup"
                r"|ops/sec)\b",
                txt,
                re.I,
            ):
                score += 0.4
            # Presence of code-like timings or tables
            if (re.search(r"\b(ms|ns|sec|seconds|ops/sec)\b",
                         txt,
                         re.I)
                    and re.search(
                r"\d", txt
            )):
                score += 0.2
            if re.search(r"\|.+\|", txt) and re.search(r"-{2,}", txt):
                score += 0.1  # Markdown table

        bench_dirs = []
        for pat in self.BENCH_GLOBS:
            bench_dirs.extend(self._glob(p, [f"**/{pat}/**"]))

        if bench_dirs:
            score += 0.3

        return self._clamp01(score)

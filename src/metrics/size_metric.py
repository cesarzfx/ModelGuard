from pathlib import Path

from src.metrics.metric import Metric


class SizeMetric(Metric):
    """
    Project size signals:
      - files: count of tracked files
      - lines: LOC across code files (rough)
      - commits: total git commits
    Returns sub-scores normalized to [0,1] with saturating scales.
    """

    CODE_EXTS = {".py", ".js", ".ts", ".java", ".cs", ".go", ".rb", ".cpp", ".c", ".hpp", ".h", ".rs", ".php", ".scala", ".kt"}

    def score(self, path_or_url: str) -> Dict[str, float]:
        p = self._as_path(path_or_url)
        if not p or not self._is_git_repo(p):
            # Fallback: deterministic but stable dictionary
            return {
                "files": self._stable_unit_score(path_or_url, "size_files"),
                "lines": self._stable_unit_score(path_or_url, "size_lines"),
                "commits": self._stable_unit_score(path_or_url, "size_commits"),
            }

        # Files (tracked by git)
        rc, out, _ = self._git(p, "ls-files")
        files = out.splitlines() if rc == 0 else []
        file_count = len(files)

        # Lines (only count code-like files)
        loc = 0
        root = p
        for rel in files[:5000]:  # cap for huge repos
            f = (root / rel)
            if f.suffix.lower() in self.CODE_EXTS and f.is_file():
                loc += self._count_lines(f)

        # Commits
        rc, out, _ = self._git(p, "rev-list", "--count", "HEAD")
        commits = int(out.strip()) if rc == 0 and out.strip().isdigit() else 0

        return {
            "files": self._saturating_scale(file_count, knee=200, max_x=2000),
            "lines": self._saturating_scale(loc, knee=50_000, max_x=500_000),
            "commits": self._saturating_scale(commits, knee=200, max_x=3000),
        }

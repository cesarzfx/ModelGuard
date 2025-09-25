from pathlib import Path
from typing import Any, List, Optional


class BaseMetric:
    def _is_git_repo(self, path: Path) -> bool:
        """Return True if path is a git repo."""
        return False

    def _git(self, *args: Any, **kwargs: Any) -> Any:
        """Run a git command and return result."""
        return None

    def _count_lines(self, path: Path) -> int:
        """Count number of lines in a file."""
        return 0

    def _saturating_scale(self, x: float, max_x: float) -> float:
        """Scale value to [0,1] with saturation at max_x."""
        return 0.0

    def _clamp01(self, x: float) -> float:
        """Clamp a float into [0,1]."""
        return 0.0

    def _read_text(self, path: Path) -> str:
        """Read text from file safely."""
        return ""

    def _glob(self, pattern: str) -> List[Path]:
        """Glob files matching pattern."""
        return []

    def _as_path(self, path_or_url: str) -> Optional[Path]:
        """Convert a string into a Path if possible."""
        return None

    def _stable_unit_score(self, key: str, salt: str) -> float:
        """Return a stable pseudo-random score between 0 and 1."""
        return 0.0

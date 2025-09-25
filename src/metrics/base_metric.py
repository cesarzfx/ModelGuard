from pathlib import Path
from typing import Any, List


class BaseMetric:
    def _is_git_repo(self, path: Path) -> bool:
        """Return True if path is a git repo."""
        ...

    def _git(self, *args: Any, **kwargs: Any) -> Any:
        """Run a git command and return result."""
        ...

    def _count_lines(self, path: Path) -> int:
        """Count number of lines in a file."""
        ...

    def _saturating_scale(self, x: float, max_x: float) -> float:
        """Scale value to [0,1] with saturation at max_x."""
        ...

    def _clamp01(self, x: float) -> float:
        """Clamp a float into [0,1]."""
        ...

    def _read_text(self, path: Path) -> str:
        """Read text from file safely."""
        ...

    def _glob(self, pattern: str) -> List[Path]:
        """Glob files matching pattern."""
        ...

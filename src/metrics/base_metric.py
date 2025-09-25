from pathlib import Path
from typing import Any, List, Optional


class BaseMetric:
    def _is_git_repo(self, path: Path) -> bool:
        return False

    def _git(self, *args: Any, **kwargs: Any) -> Any:
        return None

    def _count_lines(self, path: Path) -> int:
        return 0

    def _saturating_scale(
            self,
            x: float,
            *,
            knee: float,
            max_x: float
    ) -> float:
        """Scale value to [0,1] with a knee point and max_x saturation."""
        return 0.0

    def _clamp01(self, x: float) -> float:
        return 0.0

    def _read_text(self, path: Path) -> str:
        return ""

    def _glob(self, *args: Any, **kwargs: Any) -> List[Path]:
        """Glob files; flexible signature so mypy accepts
        different call styles."""
        return []

    def _as_path(self, path_or_url: str) -> Optional[Path]:
        return None

    def _stable_unit_score(self, key: str, salt: str) -> float:
        return 0.0

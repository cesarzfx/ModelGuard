import re

from src.metrics.metric import Metric


class RampUpMetric(Metric):
    """
    Onboarding ease:
      + README length & structure (badges, install, usage)
      + CONTRIBUTING.md presence
      + docs/ site
      + Example commands
    """

    def score(self, path_or_url: str) -> float:
        p = self._as_path(path_or_url)
        if not p:
            return self._stable_unit_score(path_or_url, "ramp_up")

        score = 0.0

        readme = None
        for name in ["README.md", "README.rst", "README.txt"]:
            f = p / name
            if f.exists():
                readme = f
                break

        if readme:
            txt = self._read_text(readme)
            length = len(txt)
            # length scaling
            if length >= 4000:
                score += 0.35
            elif length >= 1500:
                score += 0.25
            elif length >= 500:
                score += 0.15
            # badges & sections
            if re.search(r"\[!\[", txt):  # shields.io badges
                score += 0.05
            if re.search(r"\b(Install|Installation)\b", txt, re.I):
                score += 0.15
            if re.search(r"\bUsage\b", txt, re.I):
                score += 0.15
            if re.search(r"```", txt):
                score += 0.1  # code examples
        else:
            # no readme -> hard to ramp up
            return 0.05

        # contributing / docs presence
        if (p / "CONTRIBUTING.md").exists():
            score += 0.1
        if (p / "docs").exists():
            score += 0.05

        return self._clamp01(score)

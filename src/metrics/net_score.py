from statistics import fmean


class NetScore:

    name = "net_score"

    def __init__(self, url: str):
        self.url = url

    def score(self, scalar_metrics: list[float],
              size_score: dict[str, float]) -> float:
        if not scalar_metrics and not size_score:
            return 0.0

        size_mean = fmean(size_score.values()) if size_score else None
        values = scalar_metrics.copy()
        if size_mean is not None:
            values.append(size_mean)

        result = fmean(values)

        # clamp to [0, 1]
        return max(0.0, min(1.0, float(result)))

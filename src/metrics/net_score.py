from statistics import fmean


class NetScore:

    name = "net_score"

    def __init__(self, url: str):
        self.url = url

    def score(self, scalar_metrics: list[float], size_score: dict[str, float]) -> float:
        if not scalar_metrics and not size_score:
            return 0.0

        # mean of size_score values (if dict is provided)
        size_mean = fmean(size_score.values()) if size_score else 0.0

        if size_score:
            result = fmean(scalar_metrics + [size_mean])
        else:
            result = fmean(scalar_metrics)
        # clamp to [0,1]
        return max(0.0, min(1.0, float(result)))
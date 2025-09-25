import json
import sys

from src.metrics.availability_metric import AvailabilityMetric
from src.metrics.bus_factor_metric import BusFactorMetric
from src.metrics.code_quality_metric import CodeQualityMetric
from src.metrics.dataset_quality_metric import DatasetQualityMetric
from src.metrics.license_metric import LicenseMetric
from src.metrics.net_score import NetScore
from src.metrics.performance_claims_metric import PerformanceClaimsMetric
from src.metrics.ramp_up_metric import RampUpMetric
from src.metrics.size_metric import SizeMetric


def compute_all(path):
    scores = {}
    scores.update(dict(AvailabilityMetric().score(path)))
    scores.update(dict(BusFactorMetric().score(path)))
    scores.update(dict(CodeQualityMetric().score(path)))
    scores.update(dict(DatasetQualityMetric().score(path)))
    scores.update(dict(LicenseMetric().score(path)))
    scores.update(dict(PerformanceClaimsMetric().score(path)))
    scores.update(dict(RampUpMetric().score(path)))

    sz = SizeMetric().score(path)

    net = NetScore(path).combine(scores, sz)
    return {"scores": scores, "size": sz, "net_score": net}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/local/git/repo")
        sys.exit(1)
    path = sys.argv[1]
    result = compute_all(path)
    print(json.dumps(result, indent=2))

import sys
import json

from src.metrics.bus_factor_metric import BusFactorMetric
from src.metrics.code_quality_metric import CodeQualityMetric
from src.metrics.availability_metric import AvailabilityMetric
from src.metrics.dataset_quality_metric import DatasetQualityMetric
from src.metrics.license_metric import LicenseMetric
from src.metrics.performance_claims_metric import PerformanceClaimsMetric
from src.metrics.ramp_up_metric import RampUpMetric
from src.metrics.size_metric import SizeMetric
from src.metrics.net_score import NetScore



def compute_all(path):
    am = AvailabilityMetric().score(path)
    bf = BusFactorMetric().score(path)
    cq = CodeQualityMetric().score(path)
    dq = DatasetQualityMetric().score(path)
    lic = LicenseMetric().score(path)
    pc = PerformanceClaimsMetric().score(path)
    ru = RampUpMetric().score(path)
    sz = SizeMetric().score(path)


    scores = {
        "availability": am,
        "bus_factor": bf,
        "code_quality": cq,
        "dataset_quality": dq,
        "license": lic,
        "performance_claims": pc,
        "ramp_up": ru,
    }

    net = NetScore(path).combine(scores, sz)
    return {"scores": scores, "size": sz, "net_score": net}



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/local/git/repo")
        sys.exit(1)
    path = sys.argv[1]
    result = compute_all(path)
    print(json.dumps(result, indent=2))

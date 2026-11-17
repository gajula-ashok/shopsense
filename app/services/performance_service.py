import time
from typing import Dict, Any, List
from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.analytics_metadata import PerformanceTestResult
from app.models.user import User, UserRole
from app.utils.security import create_access_token

TEST_ENDPOINTS = [
    ("/api/analytics/summary", "Revenue Summary API"),
    ("/api/analytics/vendor-performance", "Vendor Performance API"),
    ("/api/analytics/customers", "Customer Analytics API"),
    ("/api/inventory/forecast", "Demand Forecasting API"),
    ("/api/recommendations/evaluation", "Recommendation Evaluation API")
]

def run_performance_benchmarks(base_url: str = "http://127.0.0.1:8000", iterations: int = 5) -> List[Dict[str, Any]]:
    """
    Executes benchmark requests against the core Milestone 3 APIs,
    recording Min, Max, Avg, P95 response times, RPS, and failure rate.
    Target: Average Response Time <= 300 ms.
    """
    db: Session = SessionLocal()
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    token = create_access_token(data={"sub": admin.email, "role": admin.role.value if hasattr(admin.role, 'value') else str(admin.role)})
    headers = {"Authorization": f"Bearer {token}"}

    results = []
    client = httpx.Client(base_url=base_url, timeout=30.0)

    for path, name in TEST_ENDPOINTS:
        latencies = []
        failures = 0
        t_start_all = time.time()

        for _ in range(iterations):
            t_req_start = time.time()
            try:
                res = client.get(path, headers=headers)
                latency_ms = (time.time() - t_req_start) * 1000.0
                if res.status_code == 200:
                    latencies.append(latency_ms)
                else:
                    failures += 1
            except Exception:
                failures += 1

        t_total = time.time() - t_start_all
        rps = round(iterations / max(0.001, t_total), 2)
        fail_pct = round((failures / iterations) * 100.0, 2)

        if latencies:
            avg_ms = round(float(sum(latencies) / len(latencies)), 2)
            min_ms = round(float(min(latencies)), 2)
            max_ms = round(float(max(latencies)), 2)
            sorted_l = sorted(latencies)
            p95_idx = int(0.95 * len(sorted_l))
            p95_ms = round(float(sorted_l[min(p95_idx, len(sorted_l) - 1)]), 2)
        else:
            avg_ms = min_ms = max_ms = p95_ms = 9999.0

        target_met = avg_ms <= 300.0 and fail_pct == 0.0
        status = "PASS" if target_met else "NEEDS IMPROVEMENT"

        entry = {
            "endpoint": path,
            "name": name,
            "avg_response_time_ms": avg_ms,
            "min_response_time_ms": min_ms,
            "max_response_time_ms": max_ms,
            "p95_response_time_ms": p95_ms,
            "requests_per_sec": rps,
            "failure_rate_pct": fail_pct,
            "status": status,
            "target_met": target_met
        }
        results.append(entry)

        # Persist test result
        try:
            p_record = PerformanceTestResult(
                test_time=datetime.now(),
                endpoint=path,
                avg_response_time_ms=avg_ms,
                min_response_time_ms=min_ms,
                max_response_time_ms=max_ms,
                p95_response_time_ms=p95_ms,
                requests_per_sec=rps,
                failure_rate_pct=fail_pct,
                status=status,
                target_met=target_met
            )
            db.add(p_record)
            db.commit()
        except Exception:
            db.rollback()

    client.close()
    db.close()
    return results

def get_performance_history(limit: int = 25) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.query(PerformanceTestResult).order_by(PerformanceTestResult.test_time.desc()).limit(limit).all()
        return [{
            "id": r.id,
            "test_time": r.test_time.strftime("%Y-%m-%d %H:%M:%S") if r.test_time else "N/A",
            "endpoint": r.endpoint,
            "avg_response_time_ms": r.avg_response_time_ms,
            "min_response_time_ms": r.min_response_time_ms,
            "max_response_time_ms": r.max_response_time_ms,
            "p95_response_time_ms": r.p95_response_time_ms,
            "requests_per_sec": r.requests_per_sec,
            "failure_rate_pct": r.failure_rate_pct,
            "status": r.status,
            "target_met": r.target_met
        } for r in rows]
    finally:
        db.close()

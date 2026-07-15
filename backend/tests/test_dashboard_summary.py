from fastapi.testclient import TestClient

from app.core.database import SessionLocal, init_db
from app.domain.models.finding import Finding
from app.domain.models.scan import Scan
from app.main import app

init_db()
client = TestClient(app)


def test_dashboard_summary_returns_counts_and_recent_scans() -> None:
    db = SessionLocal()
    db.query(Finding).delete()
    db.query(Scan).delete()
    db.add(Scan(name="Scan demo", target_url="https://example.com", status="completed", description="demo"))
    db.add(Scan(name="Scan running", target_url="https://example.org", status="running", description="demo"))
    db.add(Finding(title="SQL Injection", severity="critical", description="demo"))
    db.add(Finding(title="Missing header", severity="medium", description="demo"))
    db.commit()
    db.close()

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_scans"] == 2
    assert body["running_scans"] == 1
    assert body["total_findings"] == 2
    assert body["critical_findings"] == 1
    assert len(body["recent_scans"]) == 2

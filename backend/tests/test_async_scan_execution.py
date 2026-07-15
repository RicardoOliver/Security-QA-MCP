from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_async_scan_execution_marks_status_and_returns_execution_id() -> None:
    create_response = client.post(
        "/api/v1/scans",
        json={"name": "Async Scan", "target_url": "https://example.com", "description": "async"},
    )
    assert create_response.status_code == 200
    scan = create_response.json()

    run_response = client.post(f"/api/v1/scans/{scan['id']}/run")
    assert run_response.status_code == 200
    body = run_response.json()
    assert body["scan_id"] == scan["id"]
    assert body["status"] in {"running", "completed"}
    assert body["execution_id"]

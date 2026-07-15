from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_scan_run_updates_status_and_emits_observability() -> None:
    create_response = client.post(
        "/api/v1/scans",
        json={"name": "Execution smoke", "target_url": "https://example.com", "description": "demo"},
    )
    scan_id = create_response.json()["id"]

    response = client.post(f"/api/v1/scans/{scan_id}/run")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"running", "completed"}
    assert body["queue_length"] >= 0
    assert body["observability"]["metrics"]["scan_started"] >= 1
    assert body["observability"]["metrics"]["scan_completed"] >= 1
    assert any(event["event"] == "scan_started" for event in body["observability"]["events"])
    assert any(event["event"] == "scan_completed" for event in body["observability"]["events"])


def test_queue_status_endpoint_reports_current_queue_depth() -> None:
    response = client.get("/api/v1/scans/queue/status")
    assert response.status_code == 200
    body = response.json()
    assert "queue_length" in body
    assert body["queue_length"] >= 0


def test_scan_execution_history_and_events_are_available() -> None:
    create_response = client.post(
        "/api/v1/scans",
        json={"name": "History scan", "target_url": "https://example.org", "description": "demo"},
    )
    scan_id = create_response.json()["id"]

    run_response = client.post(f"/api/v1/scans/{scan_id}/run")
    assert run_response.status_code == 200

    history_response = client.get(f"/api/v1/scans/{scan_id}/history")
    assert history_response.status_code == 200
    history_body = history_response.json()
    assert isinstance(history_body, list)
    assert len(history_body) >= 1

    events_response = client.get(f"/api/v1/scans/{scan_id}/events")
    assert events_response.status_code == 200
    events_body = events_response.json()
    assert isinstance(events_body, list)
    assert any(event.get("event") in {"scan_started", "scan_completed"} for event in events_body)

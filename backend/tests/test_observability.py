from fastapi.testclient import TestClient

from app.core.observability import audit_trail, observer
from app.main import app

client = TestClient(app)


def test_observability_metrics_endpoint_returns_snapshot() -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    response = client.get(
        "/api/v1/observability/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "metrics" in body
    assert "events" in body


def test_audit_events_can_be_filtered_by_actor_and_action() -> None:
    audit_trail.entries.clear()
    audit_trail.record(actor="alice", action="create", resource_type="tenant", resource_id=1, details={"name": "tenant-a"})
    audit_trail.record(actor="bob", action="create", resource_type="tenant", resource_id=2, details={"name": "tenant-b"})

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    response = client.get(
        "/api/v1/audit/events",
        params={"actor": "alice", "action": "create"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["actor"] == "alice"


def test_observability_metrics_can_be_filtered_by_event() -> None:
    observer.events.clear()
    observer.metrics.clear()
    observer.scan_history.clear()
    observer.record("scan.started", {"scan_id": 1})
    observer.record("scan.completed", {"scan_id": 1})

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    response = client.get(
        "/api/v1/observability/metrics",
        params={"event": "scan.started"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["metrics"]["scan.started"] == 1
    assert len(body["events"]) == 1
    assert body["events"][0]["event"] == "scan.started"


def test_export_endpoints_return_serializable_payloads() -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    audit_response = client.get(
        "/api/v1/audit/events/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    observability_response = client.get(
        "/api/v1/observability/metrics/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    audit_csv_response = client.get(
        "/api/v1/audit/events/export?format=csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    observability_csv_response = client.get(
        "/api/v1/observability/metrics/export?format=csv",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert audit_response.status_code == 200
    assert observability_response.status_code == 200
    assert audit_csv_response.status_code == 200
    assert observability_csv_response.status_code == 200
    assert isinstance(audit_response.json(), list)
    assert "metrics" in observability_response.json()
    assert "events" in observability_response.json()
    assert "actor" in audit_csv_response.text
    assert "metric" in observability_csv_response.text.lower()

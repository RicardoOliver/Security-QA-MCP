from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_collect_scan_results_creates_findings() -> None:
    create_response = client.post(
        "/api/v1/scans",
        json={"name": "Collection smoke", "target_url": "https://example.com", "description": "demo"},
    )
    scan_id = create_response.json()["id"]

    response = client.post(f"/api/v1/scans/{scan_id}/collect")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 2
    assert body[0]["title"]
    assert all(item["scan_id"] == scan_id for item in body)

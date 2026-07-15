from fastapi.testclient import TestClient

from app.core.database import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_create_and_list_findings() -> None:
    response = client.post(
        "/api/v1/findings",
        json={"title": "Hardcoded secret", "severity": "critical", "description": "test"},
    )
    assert response.status_code == 200

    list_response = client.get("/api/v1/findings")
    assert list_response.status_code == 200
    assert isinstance(list_response.json(), list)

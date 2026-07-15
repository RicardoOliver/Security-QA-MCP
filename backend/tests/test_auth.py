from fastapi.testclient import TestClient

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.domain.models.user import User
from app.main import app

init_db()
client = TestClient(app)


def test_login_returns_token_for_valid_credentials() -> None:
    db = SessionLocal()
    db.query(User).delete()
    db.add(User(username="admin", password_hash=hash_password("password123"), is_active=True))
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_me_requires_token() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_enterprise_routes_require_authentication() -> None:
    response = client.post(
        "/api/v1/tenants",
        json={"name": "Acme", "slug": "acme-auth-test", "description": "Example tenant"},
    )
    assert response.status_code == 401

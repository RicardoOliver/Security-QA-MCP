from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domain.models.user import User
from app.main import app

client = TestClient(app)


def test_jwt_authentication_can_issue_and_validate_tokens() -> None:
    db = SessionLocal()
    db.query(User).delete()
    db.add(User(username="admin", password_hash=hash_password("password123"), is_active=True))
    db.commit()
    db.close()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"


def test_inactive_users_cannot_login() -> None:
    db = SessionLocal()
    db.query(User).delete()
    db.add(User(username="inactive", password_hash=hash_password("password123"), is_active=False))
    db.commit()
    db.close()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "inactive", "password": "password123"},
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Inactive user"

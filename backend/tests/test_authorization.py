from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domain.models.permission import Permission
from app.domain.models.role import Role
from app.domain.models.user import User
from app.main import app

client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    db = SessionLocal()
    db.query(User).delete()
    db.add(User(username="admin", password_hash=hash_password("password123"), is_active=True))
    db.commit()
    db.close()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_role_and_permission_can_be_created_and_checked() -> None:
    db = SessionLocal()
    db.query(Permission).delete()
    db.query(Role).delete()
    db.commit()
    db.close()

    role_response = client.post(
        "/api/v1/roles",
        json={"name": "security_admin", "description": "Admin"},
        headers=_auth_headers(),
    )
    assert role_response.status_code == 201
    role_body = role_response.json()
    assert role_body["name"] == "security_admin"

    permission_response = client.post(
        "/api/v1/permissions",
        json={"name": "scan:create", "description": "Create scans"},
        headers=_auth_headers(),
    )
    assert permission_response.status_code == 201
    permission_body = permission_response.json()
    assert permission_body["name"] == "scan:create"

    assign_response = client.post(
        "/api/v1/roles/" + str(role_body["id"]) + "/permissions",
        json={"permission_id": permission_body["id"]},
        headers=_auth_headers(),
    )
    assert assign_response.status_code == 200

    access_response = client.get(
        "/api/v1/roles/" + str(role_body["id"]) + "/permissions",
        headers=_auth_headers(),
    )
    assert access_response.status_code == 200
    assert any(item["name"] == "scan:create" for item in access_response.json())

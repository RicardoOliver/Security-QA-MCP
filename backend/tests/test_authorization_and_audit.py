from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domain.models.user import User
from app.main import app

client = TestClient(app)


def test_regular_user_cannot_access_tenants() -> None:
    db = SessionLocal()
    db.add(User(username="viewer", password_hash=hash_password("secret123"), is_active=True))
    db.commit()
    db.close()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "viewer", "password": "secret123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    response = client.get(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_audit_events_are_recorded_for_tenant_creation() -> None:
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert admin_login.status_code == 200

    token = admin_login.json()["access_token"]
    create_response = client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Audit tenant", "slug": "audit-tenant", "description": "audit"},
    )
    assert create_response.status_code == 201

    audit_response = client.get(
        "/api/v1/audit/events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert audit_response.status_code == 200
    assert any(event["resource_type"] == "tenant" for event in audit_response.json())

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domain.models.tenant import Tenant
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


def test_tenant_project_environment_and_target_can_be_created() -> None:
    db = SessionLocal()
    db.query(Tenant).delete()
    db.commit()
    db.close()

    tenant_response = client.post(
        "/api/v1/tenants",
        json={"name": "Acme Corp", "slug": "acme", "description": "Enterprise tenant"},
        headers=_auth_headers(),
    )
    assert tenant_response.status_code == 201
    tenant_body = tenant_response.json()
    assert tenant_body["slug"] == "acme"

    project_response = client.post(
        "/api/v1/projects",
        json={"name": "Payments API", "tenant_id": tenant_body["id"], "description": "Core platform"},
        headers=_auth_headers(),
    )
    assert project_response.status_code == 201
    project_body = project_response.json()
    assert project_body["tenant_id"] == tenant_body["id"]

    environment_response = client.post(
        "/api/v1/environments",
        json={"name": "Production", "project_id": project_body["id"], "description": "Prod"},
        headers=_auth_headers(),
    )
    assert environment_response.status_code == 201
    environment_body = environment_response.json()
    assert environment_body["project_id"] == project_body["id"]

    target_response = client.post(
        "/api/v1/targets",
        json={
            "name": "API Gateway",
            "url": "https://api.acme.example",
            "project_id": project_body["id"],
            "environment_id": environment_body["id"],
            "description": "Entry point",
        },
        headers=_auth_headers(),
    )
    assert target_response.status_code == 201
    target_body = target_response.json()
    assert target_body["project_id"] == project_body["id"]

    list_response = client.get("/api/v1/projects", headers=_auth_headers())
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

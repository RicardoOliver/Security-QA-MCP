from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.domain.models.environment import Environment
from app.domain.models.project import Project
from app.domain.models.target import Target
from app.domain.models.tenant import Tenant
from app.main import app

client = TestClient(app)


def test_create_and_list_scans() -> None:
    response = client.post(
        "/api/v1/scans",
        json={"name": "API smoke test", "target_url": "https://example.com", "description": "smoke"},
    )
    assert response.status_code == 200

    list_response = client.get("/api/v1/scans")
    assert list_response.status_code == 200
    body = list_response.json()
    assert isinstance(body, list)
    assert body[0]["name"] == "API smoke test"


def test_create_scan_with_target_id_uses_target_url() -> None:
    db = SessionLocal()
    tenant = Tenant(name="Target tenant", slug="target-tenant")
    project = Project(name="Target project", tenant_id=1, description="")
    environment = Environment(name="Target environment", project_id=1, description="")
    target = Target(name="Target app", url="https://target.example", project_id=1, environment_id=1, description="")

    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    project.tenant_id = tenant.id
    environment.project_id = 1 if tenant.id == 1 else tenant.id
    db.add(project)
    db.add(environment)
    db.commit()
    db.refresh(project)
    db.refresh(environment)

    target.project_id = project.id
    target.environment_id = environment.id
    db.add(target)
    db.commit()
    db.refresh(target)
    db.close()

    response = client.post(
        "/api/v1/scans",
        json={"name": "Target-backed scan", "target_url": "https://manual.example", "target_id": target.id, "description": "target"},
    )

    assert response.status_code == 200
    assert response.json()["target_url"] == "https://target.example"

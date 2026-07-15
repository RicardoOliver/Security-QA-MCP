import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.application.use_cases.collect_scan_results import CollectScanResultsUseCase
from app.application.use_cases.create_finding import CreateFindingUseCase
from app.application.use_cases.create_scan import CreateScanUseCase
from app.application.use_cases.run_scan import RunScanUseCase
from app.core.database import get_db
from app.core.observability import audit_trail, observer
from app.infrastructure.repositories.environment_repository import EnvironmentRepository
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.permission_repository import PermissionRepository
from app.infrastructure.repositories.project_repository import ProjectRepository
from app.infrastructure.repositories.role_repository import RoleRepository
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.repositories.target_repository import TargetRepository
from app.infrastructure.repositories.tenant_repository import TenantRepository
from app.interfaces.api.v1.auth_router import get_current_user
from app.interfaces.api.v1.schemas import (
    DashboardSummaryResponse,
    EnvironmentCreate,
    EnvironmentOut,
    FindingCreate,
    FindingOut,
    PermissionCreate,
    PermissionOut,
    ProjectCreate,
    ProjectOut,
    RoleCreate,
    RoleOut,
    RolePermissionAssign,
    ScanCreate,
    ScanOut,
    TargetCreate,
    TargetOut,
    TenantCreate,
    TenantOut,
    UserResponse,
)

api_router = APIRouter()


def require_permission(current_user: UserResponse, permission: str) -> None:
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")


@api_router.post("/findings", response_model=FindingOut, tags=["findings"])
def create_finding(payload: FindingCreate, db: Session = Depends(get_db)) -> FindingOut:
    repository = FindingRepository(db)
    use_case = CreateFindingUseCase(repository)
    finding = use_case.execute(payload.title, payload.severity, payload.description)
    return FindingOut(id=finding.id, scan_id=finding.scan_id, title=finding.title, severity=finding.severity, description=finding.description)


@api_router.get("/findings", response_model=list[FindingOut], tags=["findings"])
def list_findings(db: Session = Depends(get_db)) -> list[FindingOut]:
    repository = FindingRepository(db)
    findings = repository.list_all()
    return [
        FindingOut(id=finding.id, scan_id=finding.scan_id, title=finding.title, severity=finding.severity, description=finding.description)
        for finding in findings
    ]


@api_router.post("/scans", response_model=ScanOut, tags=["scans"])
def create_scan(payload: ScanCreate, db: Session = Depends(get_db)) -> ScanOut:
    repository = ScanRepository(db)
    target_repository = TargetRepository(db)
    use_case = CreateScanUseCase(repository)
    scan = use_case.execute(payload.name, payload.target_url, payload.description, payload.target_id, target_repository)
    return ScanOut(
        id=scan.id,
        name=scan.name,
        target_url=scan.target_url,
        status=scan.status,
        description=scan.description,
        created_at=scan.created_at.isoformat() if scan.created_at else "",
        updated_at=scan.updated_at.isoformat() if scan.updated_at else "",
        findings_count=scan.findings_count or 0,
    )


@api_router.get("/scans", response_model=list[ScanOut], tags=["scans"])
def list_scans(db: Session = Depends(get_db)) -> list[ScanOut]:
    repository = ScanRepository(db)
    scans = repository.list_all()
    return [
        ScanOut(
            id=scan.id,
            name=scan.name,
            target_url=scan.target_url,
            status=scan.status,
            description=scan.description,
            created_at=scan.created_at.isoformat() if scan.created_at else "",
            updated_at=scan.updated_at.isoformat() if scan.updated_at else "",
            findings_count=scan.findings_count or 0,
        )
        for scan in scans
    ]


@api_router.post("/scans/{scan_id}/run", tags=["scans"])
def run_scan(scan_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    repository = ScanRepository(db)
    use_case = RunScanUseCase(repository)
    return use_case.execute(scan_id)


@api_router.get("/scans/queue/status", tags=["scans"])
def get_scan_queue_status() -> dict[str, object]:
    from app.application.use_cases.run_scan import InMemoryScanQueue

    queue = InMemoryScanQueue()
    return {"queue_length": queue.size(), "status": "active"}


@api_router.get("/scans/{scan_id}/history", tags=["scans"])
def get_scan_history(scan_id: int) -> list[dict[str, object]]:
    return observer.history_for_scan(scan_id)


@api_router.get("/scans/{scan_id}/events", tags=["scans"])
def get_scan_events(scan_id: int) -> list[dict[str, object]]:
    return observer.events_for_scan(scan_id)


@api_router.post("/scans/{scan_id}/collect", response_model=list[FindingOut], tags=["scans"])
def collect_scan_results(scan_id: int, db: Session = Depends(get_db)) -> list[FindingOut]:
    scan_repository = ScanRepository(db)
    finding_repository = FindingRepository(db)
    use_case = CollectScanResultsUseCase(scan_repository, finding_repository)
    findings = use_case.execute(scan_id)
    return [
        FindingOut(id=finding.id, scan_id=finding.scan_id, title=finding.title, severity=finding.severity, description=finding.description)
        for finding in findings
    ]


@api_router.post("/tenants", response_model=TenantOut, status_code=201, tags=["tenants"])
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> TenantOut:
    require_permission(current_user, "tenant:create")
    from app.domain.models.tenant import Tenant

    repository = TenantRepository(db)
    tenant = Tenant(name=payload.name, slug=payload.slug, description=payload.description)
    created = repository.create(tenant)
    audit_trail.record(actor=current_user.username, action="create", resource_type="tenant", resource_id=created.id, details={"name": created.name})
    return TenantOut(id=created.id, name=created.name, slug=created.slug, description=created.description)


@api_router.get("/tenants", response_model=list[TenantOut], tags=["tenants"])
def list_tenants(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[TenantOut]:
    require_permission(current_user, "tenant:read")
    repository = TenantRepository(db)
    tenants = repository.list_all()
    return [TenantOut(id=tenant.id, name=tenant.name, slug=tenant.slug, description=tenant.description) for tenant in tenants]


@api_router.post("/projects", response_model=ProjectOut, status_code=201, tags=["projects"])
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> ProjectOut:
    from app.domain.models.project import Project

    repository = ProjectRepository(db)
    project = Project(name=payload.name, tenant_id=payload.tenant_id, description=payload.description)
    created = repository.create(project)
    return ProjectOut(id=created.id, name=created.name, tenant_id=created.tenant_id, description=created.description)


@api_router.get("/projects", response_model=list[ProjectOut], tags=["projects"])
def list_projects(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[ProjectOut]:
    repository = ProjectRepository(db)
    projects = repository.list_all()
    return [ProjectOut(id=project.id, name=project.name, tenant_id=project.tenant_id, description=project.description) for project in projects]


@api_router.post("/environments", response_model=EnvironmentOut, status_code=201, tags=["environments"])
def create_environment(
    payload: EnvironmentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> EnvironmentOut:
    from app.domain.models.environment import Environment

    repository = EnvironmentRepository(db)
    environment = Environment(name=payload.name, project_id=payload.project_id, description=payload.description)
    created = repository.create(environment)
    return EnvironmentOut(id=created.id, name=created.name, project_id=created.project_id, description=created.description)


@api_router.get("/environments", response_model=list[EnvironmentOut], tags=["environments"])
def list_environments(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[EnvironmentOut]:
    repository = EnvironmentRepository(db)
    environments = repository.list_all()
    return [EnvironmentOut(id=environment.id, name=environment.name, project_id=environment.project_id, description=environment.description) for environment in environments]


@api_router.post("/targets", response_model=TargetOut, status_code=201, tags=["targets"])
def create_target(
    payload: TargetCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> TargetOut:
    from app.domain.models.target import Target

    repository = TargetRepository(db)
    target = Target(
        name=payload.name,
        url=payload.url,
        project_id=payload.project_id,
        environment_id=payload.environment_id,
        description=payload.description,
    )
    created = repository.create(target)
    return TargetOut(
        id=created.id,
        name=created.name,
        url=created.url,
        project_id=created.project_id,
        environment_id=created.environment_id,
        description=created.description,
    )


@api_router.get("/targets", response_model=list[TargetOut], tags=["targets"])
def list_targets(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[TargetOut]:
    repository = TargetRepository(db)
    targets = repository.list_all()
    return [
        TargetOut(
            id=target.id,
            name=target.name,
            url=target.url,
            project_id=target.project_id,
            environment_id=target.environment_id,
            description=target.description,
        )
        for target in targets
    ]


@api_router.post("/roles", response_model=RoleOut, status_code=201, tags=["roles"])
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> RoleOut:
    from app.domain.models.role import Role

    repository = RoleRepository(db)
    role = Role(name=payload.name, description=payload.description)
    created = repository.create(role)
    return RoleOut(id=created.id, name=created.name, description=created.description)


@api_router.get("/roles", response_model=list[RoleOut], tags=["roles"])
def list_roles(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[RoleOut]:
    repository = RoleRepository(db)
    roles = repository.list_all()
    return [RoleOut(id=role.id, name=role.name, description=role.description) for role in roles]


@api_router.post("/permissions", response_model=PermissionOut, status_code=201, tags=["permissions"])
def create_permission(
    payload: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> PermissionOut:
    from app.domain.models.permission import Permission

    repository = PermissionRepository(db)
    permission = Permission(name=payload.name, description=payload.description)
    created = repository.create(permission)
    return PermissionOut(id=created.id, name=created.name, description=created.description)


@api_router.get("/permissions", response_model=list[PermissionOut], tags=["permissions"])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[PermissionOut]:
    repository = PermissionRepository(db)
    permissions = repository.list_all()
    return [PermissionOut(id=permission.id, name=permission.name, description=permission.description) for permission in permissions]


@api_router.post("/roles/{role_id}/permissions", response_model=list[PermissionOut], tags=["roles"])
def assign_permission(
    role_id: int,
    payload: RolePermissionAssign,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[PermissionOut]:
    repository = RoleRepository(db)
    repository.add_permission(role_id, payload.permission_id)
    permissions = repository.list_permissions(role_id)
    return [PermissionOut(id=permission.id, name=permission.name, description=permission.description) for permission in permissions]


@api_router.get("/audit/events", response_model=list[dict[str, object]], tags=["audit"])
def list_audit_events(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    actor: str | None = None,
    action: str | None = None,
) -> list[dict[str, object]]:
    require_permission(current_user, "audit:read")
    return audit_trail.list(actor=actor, action=action)


@api_router.get("/audit/events/export", response_model=None, tags=["audit"])
def export_audit_events(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    format: str | None = None,
    actor: str | None = None,
    action: str | None = None,
) -> list[dict[str, object]] | Response:
    require_permission(current_user, "audit:read")
    entries = audit_trail.list(actor=actor, action=action)
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["actor", "action", "resource_type", "resource_id", "details"])
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)
        payload = output.getvalue()
        return Response(content=payload, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit-events.csv"})
    return entries


@api_router.get("/observability/metrics", tags=["observability"])
def observability_metrics(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    event: str | None = None,
) -> dict[str, object]:
    require_permission(current_user, "observability:read")
    snapshot = observer.snapshot(event=event)
    return {"events": snapshot["events"], "metrics": snapshot["metrics"]}


@api_router.get("/observability/metrics/export", response_model=None, tags=["observability"])
def export_observability_metrics(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    format: str | None = None,
    event: str | None = None,
) -> dict[str, object] | Response:
    require_permission(current_user, "observability:read")
    snapshot = observer.snapshot(event=event)
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["metric", "count"])
        for metric, count in snapshot["metrics"].items():
            writer.writerow([metric, count])
        payload = output.getvalue()
        return Response(content=payload, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=observability-metrics.csv"})
    return snapshot


@api_router.get("/roles/{role_id}/permissions", response_model=list[PermissionOut], tags=["roles"])
def list_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[PermissionOut]:
    repository = RoleRepository(db)
    permissions = repository.list_permissions(role_id)
    return [PermissionOut(id=permission.id, name=permission.name, description=permission.description) for permission in permissions]


@api_router.get("/dashboard/summary", response_model=DashboardSummaryResponse, tags=["dashboard"])
def dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummaryResponse:
    scan_repository = ScanRepository(db)
    finding_repository = FindingRepository(db)

    scans = scan_repository.list_all()
    findings = finding_repository.list_all()

    return DashboardSummaryResponse(
        total_scans=len(scans),
        running_scans=sum(1 for scan in scans if scan.status == "running"),
        total_findings=len(findings),
        critical_findings=sum(1 for finding in findings if finding.severity == "critical"),
        recent_scans=[
            ScanOut(
                id=scan.id,
                name=scan.name,
                target_url=scan.target_url,
                status=scan.status,
                description=scan.description,
                created_at=scan.created_at.isoformat() if scan.created_at else "",
                updated_at=scan.updated_at.isoformat() if scan.updated_at else "",
                findings_count=scan.findings_count or 0,
            )
            for scan in scans[:5]
        ],
    )

from pydantic import BaseModel, ConfigDict


class FindingCreate(BaseModel):
    title: str
    severity: str = "medium"
    description: str = ""


class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scan_id: int | None = None
    title: str
    severity: str
    description: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str


class ScanCreate(BaseModel):
    name: str
    target_url: str = ""
    target_id: int | None = None
    description: str = ""


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_url: str
    status: str
    description: str
    created_at: str
    updated_at: str
    findings_count: int


class TenantCreate(BaseModel):
    name: str
    slug: str
    description: str = ""


class TenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str


class ProjectCreate(BaseModel):
    name: str
    tenant_id: int
    description: str = ""


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    tenant_id: int
    description: str


class EnvironmentCreate(BaseModel):
    name: str
    project_id: int
    description: str = ""


class EnvironmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    project_id: int
    description: str


class TargetCreate(BaseModel):
    name: str
    url: str
    project_id: int
    environment_id: int
    description: str = ""


class TargetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    project_id: int
    environment_id: int
    description: str


class RoleCreate(BaseModel):
    name: str
    description: str = ""


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class PermissionCreate(BaseModel):
    name: str
    description: str = ""


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class RolePermissionAssign(BaseModel):
    permission_id: int


class DashboardSummaryResponse(BaseModel):
    total_scans: int
    running_scans: int
    total_findings: int
    critical_findings: int
    recent_scans: list[ScanOut]

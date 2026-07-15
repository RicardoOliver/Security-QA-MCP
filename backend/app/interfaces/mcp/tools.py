from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.interfaces.api.v1.schemas import ScanCreate, ScanOut

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/tools")
def list_mcp_tools() -> list[dict[str, str]]:
    return [
        {"name": "list_scans", "description": "List available scans"},
        {"name": "create_scan", "description": "Create a new scan"},
    ]


@router.post("/tools/create_scan")
def create_scan_tool(payload: ScanCreate, db: Session = Depends(get_db)) -> ScanOut:
    from app.application.use_cases.create_scan import CreateScanUseCase

    repository = ScanRepository(db)
    use_case = CreateScanUseCase(repository)
    scan = use_case.execute(payload.name, payload.target_url, payload.description)
    return ScanOut(id=scan.id, name=scan.name, target_url=scan.target_url, status=scan.status, description=scan.description)


@router.get("/tools/list_scans")
def list_scans_tool(db: Session = Depends(get_db)) -> list[ScanOut]:
    repository = ScanRepository(db)
    scans = repository.list_all()
    return [
        ScanOut(id=scan.id, name=scan.name, target_url=scan.target_url, status=scan.status, description=scan.description)
        for scan in scans
    ]

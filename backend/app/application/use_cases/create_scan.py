from datetime import datetime

from app.domain.models.scan import Scan
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.repositories.target_repository import TargetRepository


class CreateScanUseCase:
    def __init__(self, repository: ScanRepository):
        self.repository = repository

    def execute(self, name: str, target_url: str, description: str = "", target_id: int | None = None, target_repository: TargetRepository | None = None) -> Scan:
        resolved_target_url = target_url
        if target_id is not None and target_repository is not None:
            target = target_repository.get_by_id(target_id)
            if target is not None:
                resolved_target_url = target.url

        now = datetime.utcnow()
        scan = Scan(
            name=name,
            target_url=resolved_target_url,
            description=description,
            status="pending",
            created_at=now,
            updated_at=now,
        )
        return self.repository.create(scan)

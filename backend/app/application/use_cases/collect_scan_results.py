from datetime import datetime

from app.domain.models.finding import Finding
from app.infrastructure.repositories.finding_repository import FindingRepository
from app.infrastructure.repositories.scan_repository import ScanRepository
from app.infrastructure.scanners.demo_scanner import DemoScannerAdapter


class CollectScanResultsUseCase:
    def __init__(self, scan_repository: ScanRepository, finding_repository: FindingRepository, scanner: DemoScannerAdapter | None = None):
        self.scan_repository = scan_repository
        self.finding_repository = finding_repository
        self.scanner = scanner or DemoScannerAdapter()

    def execute(self, scan_id: int) -> list[Finding]:
        scan = self.scan_repository.get_by_id(scan_id)
        if not scan:
            raise ValueError("Scan not found")

        findings_payload = self.scanner.run(scan.target_url)
        created: list[Finding] = []
        for item in findings_payload:
            finding = self.finding_repository.create(
                Finding(
                    scan_id=scan.id,
                    title=item["title"],
                    severity=item["severity"],
                    description=item["description"],
                )
            )
            created.append(finding)

        scan.findings_count = len(created)
        scan.updated_at = datetime.utcnow()
        self.scan_repository.update(scan)

        return created

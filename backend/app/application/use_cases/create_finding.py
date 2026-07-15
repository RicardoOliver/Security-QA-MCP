from app.domain.models.finding import Finding
from app.infrastructure.repositories.finding_repository import FindingRepository


class CreateFindingUseCase:
    def __init__(self, repository: FindingRepository):
        self.repository = repository

    def execute(self, title: str, severity: str, description: str) -> Finding:
        finding = Finding(title=title, severity=severity, description=description)
        return self.repository.create(finding)

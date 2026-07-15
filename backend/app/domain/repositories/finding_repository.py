from abc import ABC, abstractmethod

from app.domain.models.finding import Finding


class FindingRepositoryPort(ABC):
    @abstractmethod
    def create(self, finding: Finding) -> Finding:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Finding]:
        raise NotImplementedError

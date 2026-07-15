from abc import ABC, abstractmethod

from app.domain.models.scan import Scan


class ScanRepositoryPort(ABC):
    @abstractmethod
    def create(self, scan: Scan) -> Scan:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Scan]:
        raise NotImplementedError

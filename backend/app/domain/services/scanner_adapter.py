from abc import ABC, abstractmethod


class ScannerAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, target_url: str) -> list[dict[str, str]]:
        raise NotImplementedError

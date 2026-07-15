from __future__ import annotations

from abc import ABC, abstractmethod


class ScannerAdapter(ABC):
    @abstractmethod
    def run(self, target_url: str) -> list[dict[str, object]]:
        raise NotImplementedError

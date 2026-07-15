from __future__ import annotations

import os

from app.infrastructure.scanners.base import ScannerAdapter
from app.infrastructure.scanners.custom_rest_scanner import CustomRestScannerAdapter
from app.infrastructure.scanners.http_scanner import HttpScannerAdapter


class ScannerAdapterFactory:
    @staticmethod
    def build() -> ScannerAdapter:
        scanner_type = os.getenv("SECURITY_QA_SCANNER_TYPE", "disabled")
        if scanner_type == "http":
            return HttpScannerAdapter()
        if scanner_type == "custom_rest":
            return CustomRestScannerAdapter()
        return DisabledScannerAdapter()


class DisabledScannerAdapter(ScannerAdapter):
    def run(self, target_url: str) -> list[dict[str, object]]:
        return []

from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from app.infrastructure.scanners.base import ScannerAdapter


class CustomRestScannerAdapter(ScannerAdapter):
    def __init__(self, endpoint: str | None = None, timeout: int | None = None) -> None:
        self.endpoint = endpoint or os.getenv("SECURITY_QA_CUSTOM_REST_SCANNER_URL", "")
        self.timeout = timeout or int(os.getenv("SECURITY_QA_CUSTOM_REST_SCANNER_TIMEOUT", "5"))

    def run(self, target_url: str) -> list[dict[str, object]]:
        if not self.endpoint:
            return []

        payload = {"target": target_url, "source": "security_qa_mcp"}
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(self.endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with request.urlopen(req, timeout=self.timeout) as response:
            body = response.read().decode("utf-8")
            response_payload = json.loads(body)

        findings = response_payload.get("findings", [])
        return [
            {
                "title": finding.get("title", "Custom REST finding"),
                "severity": finding.get("severity", "medium"),
                "description": finding.get("description", ""),
            }
            for finding in findings
        ]

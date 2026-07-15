from app.domain.services.scanner_adapter import ScannerAdapter


class DemoScannerAdapter(ScannerAdapter):
    name = "demo"

    def run(self, target_url: str) -> list[dict[str, str]]:
        return [
            {
                "title": "Missing security headers",
                "severity": "medium",
                "description": f"The target {target_url} does not expose recommended security headers.",
            },
            {
                "title": "TLS configuration warning",
                "severity": "high",
                "description": f"The target {target_url} should enforce modern TLS settings.",
            },
        ]

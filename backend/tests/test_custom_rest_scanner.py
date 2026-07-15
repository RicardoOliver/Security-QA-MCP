import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.infrastructure.scanners.custom_rest_scanner import CustomRestScannerAdapter


class CustomRestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        payload = {
            "findings": [
                {
                    "title": "Custom REST issue",
                    "severity": "critical",
                    "description": "Imported from custom REST scanner",
                }
            ]
        }
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def test_custom_rest_scanner_adapter_imports_findings() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), CustomRestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        os.environ["SECURITY_QA_CUSTOM_REST_SCANNER_URL"] = f"http://127.0.0.1:{server.server_port}/scan"
        os.environ["SECURITY_QA_CUSTOM_REST_SCANNER_TIMEOUT"] = "5"

        adapter = CustomRestScannerAdapter()
        findings = adapter.run("https://example.com")

        assert len(findings) == 1
        assert findings[0]["title"] == "Custom REST issue"
        assert findings[0]["severity"] == "critical"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        os.environ.pop("SECURITY_QA_CUSTOM_REST_SCANNER_URL", None)
        os.environ.pop("SECURITY_QA_CUSTOM_REST_SCANNER_TIMEOUT", None)

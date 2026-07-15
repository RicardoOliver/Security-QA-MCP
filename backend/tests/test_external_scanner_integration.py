import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class ScannerHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        payload = json.loads(body)
        self.server.last_payload = payload  # type: ignore[attr-defined]
        response_payload = {
            "findings": [
                {
                    "title": "External scanner finding",
                    "severity": "high",
                    "description": f"Discovered for {payload.get('target', 'unknown')}",
                }
            ]
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_payload).encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def test_external_scanner_adapter_creates_findings_for_run() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), ScannerHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        os.environ["SECURITY_QA_SCANNER_TYPE"] = "http"
        os.environ["SECURITY_QA_SCANNER_URL"] = f"http://127.0.0.1:{server.server_port}/scan"
        os.environ["SECURITY_QA_SCANNER_TIMEOUT"] = "5"

        create_response = client.post(
            "/api/v1/scans",
            json={"name": "External scan", "target_url": "https://example.com", "description": "demo"},
        )
        assert create_response.status_code == 200
        scan_id = create_response.json()["id"]

        response = client.post(f"/api/v1/scans/{scan_id}/run")
        assert response.status_code == 200

        findings_response = client.get("/api/v1/findings")
        assert findings_response.status_code == 200
        findings = findings_response.json()
        assert any(item["scan_id"] == scan_id and item["title"] == "External scanner finding" for item in findings)
    finally:
        server.shutdown()
        thread.join(timeout=5)
        os.environ.pop("SECURITY_QA_SCANNER_TYPE", None)
        os.environ.pop("SECURITY_QA_SCANNER_URL", None)
        os.environ.pop("SECURITY_QA_SCANNER_TIMEOUT", None)

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mcp_tools_expose_scan_operations() -> None:
    response = client.get("/mcp/tools")
    assert response.status_code == 200
    body = response.json()
    assert any(tool["name"] == "list_scans" for tool in body)
    assert any(tool["name"] == "create_scan" for tool in body)


import os
from fastapi.testclient import TestClient

from backend.app import app


def test_scan_detects_demo_secret_leak():
    os.environ["LLM_PROVIDER"] = "demo"

    client = TestClient(app)
    response = client.post("/scan")

    assert response.status_code == 200

    report = response.json()
    assert report["summary"]["total"] == 2
    assert report["summary"]["failed"] == 2
    assert all(
        result["status"] == "FAIL"
        for result in report["results"]
    )


def test_scan_report_contains_evidence():
    os.environ["LLM_PROVIDER"] = "demo"

    client = TestClient(app)
    response = client.post("/scan")

    assert response.status_code == 200
    report = response.json()

    for result in report["results"]:
        assert result["id"]
        assert result["evidence"]
        assert result["recommendation"]

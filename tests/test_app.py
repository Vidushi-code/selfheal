import json

from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_incidents_average(tmp_path, monkeypatch):
    log = tmp_path / "incidents.jsonl"
    log.write_text(
        json.dumps({"type": "container_down", "recovery_seconds": 4}) + "\n"
        + json.dumps({"type": "nginx_down", "recovery_seconds": 6}) + "\n"
    )
    monkeypatch.setattr(main, "LOG_FILE", log)
    data = client.get("/incidents").json()
    assert data["total_incidents"] == 2
    assert data["average_recovery_seconds"] == 5.0
import json
import os
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="SelfHeal")

LOG_FILE = Path(os.getenv("INCIDENT_LOG", "/data/incidents.jsonl"))
VERSION = os.getenv("APP_VERSION", "dev")


def read_incidents():
    if not LOG_FILE.exists():
        return []
    incidents = []
    for line in LOG_FILE.read_text().splitlines():
        try:
            incidents.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # skip a broken line, never crash
    return incidents


@app.get("/")
def home():
    return {"app": "SelfHeal", "status": "running", "version": VERSION}


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.get("/incidents")
def incidents():
    items = read_incidents()
    times = [i["recovery_seconds"] for i in items if "recovery_seconds" in i]
    avg = round(sum(times) / len(times), 2) if times else None
    return {
        "total_incidents": len(items),
        "average_recovery_seconds": avg,
        "recent": items[-10:][::-1],  # newest first
    }
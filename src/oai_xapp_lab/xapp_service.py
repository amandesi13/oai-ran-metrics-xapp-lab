from __future__ import annotations

from contextlib import asynccontextmanager
import os
import threading
import time

import requests
import uvicorn
from fastapi import FastAPI, Response

from .detector import detect_anomalies
from .models import RanAlert, RanSnapshot
from .prometheus_exporter import RanPrometheusExporter

SOURCE_URL = os.getenv("RAN_SOURCE_URL", "http://localhost:8100/ran-metrics")
POLL_INTERVAL_SECONDS = float(os.getenv("POLL_INTERVAL_SECONDS", "2"))
SCENARIO = os.getenv("RAN_SCENARIO", "normal")

exporter = RanPrometheusExporter()
latest_snapshot: RanSnapshot | None = None
latest_alerts: list[RanAlert] = []
collector_started = False


def collect_once() -> tuple[RanSnapshot, list[RanAlert]]:
    response = requests.get(SOURCE_URL, params={"scenario": SCENARIO}, timeout=5)
    response.raise_for_status()
    snapshot = RanSnapshot.model_validate(response.json())
    alerts = detect_anomalies(snapshot)
    exporter.update(snapshot, alerts)
    return snapshot, alerts


def collector_loop() -> None:
    global latest_snapshot, latest_alerts
    while True:
        try:
            latest_snapshot, latest_alerts = collect_once()
        except Exception as exc:  # pragma: no cover - operational resilience
            print(f"xApp collection failed: {exc}", flush=True)
        time.sleep(POLL_INTERVAL_SECONDS)


def start_collector() -> None:
    global collector_started
    if collector_started:
        return
    collector_started = True
    thread = threading.Thread(target=collector_loop, daemon=True)
    thread.start()


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_collector()
    yield


app = FastAPI(title="RAN Metrics xApp", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "source": SOURCE_URL}


@app.get("/snapshot")
def snapshot():
    if latest_snapshot is None:
        return {"status": "warming-up"}
    return latest_snapshot.model_dump(mode="json")


@app.get("/alerts")
def alerts():
    return [alert.model_dump(mode="json") for alert in latest_alerts]


@app.get("/metrics")
def prometheus_metrics() -> Response:
    return Response(content=exporter.render(), media_type="text/plain; version=0.0.4")


def main() -> None:
    uvicorn.run("oai_xapp_lab.xapp_service:app", host="0.0.0.0", port=int(os.getenv("PORT", "8101")), reload=False)


if __name__ == "__main__":  # pragma: no cover
    main()

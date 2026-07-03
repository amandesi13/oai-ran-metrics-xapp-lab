from __future__ import annotations

import os

import uvicorn
from fastapi import FastAPI, Query

from .simulator import OaiRanSimulator

app = FastAPI(title="OAI-inspired RAN Metrics Source", version="0.1.0")
simulator = OaiRanSimulator(seed=int(os.getenv("RAN_SIM_SEED", "42")))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ran-metrics")
def metrics_json(scenario: str = Query(default="normal", pattern="^(normal|congestion|radio-degradation)$")):
    return simulator.snapshot(scenario=scenario).model_dump(mode="json")


def main() -> None:
    uvicorn.run("oai_xapp_lab.source_app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8100")), reload=False)


if __name__ == "__main__":  # pragma: no cover
    main()

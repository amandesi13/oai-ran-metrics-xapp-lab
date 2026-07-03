from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class CellMetrics(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    gnb_id: str
    cell_id: str
    dl_prb_utilization: float = Field(ge=0, le=100)
    ul_prb_utilization: float = Field(ge=0, le=100)
    active_ues: int = Field(ge=0)
    avg_dl_throughput_mbps: float = Field(ge=0)
    avg_ul_throughput_mbps: float = Field(ge=0)
    avg_latency_ms: float = Field(ge=0)
    packet_loss_pct: float = Field(ge=0, le=100)
    rrc_connected_ues: int = Field(ge=0)
    handover_failures: int = Field(ge=0)
    pusch_sinr_db: float
    pucch_sinr_db: float


class UeMetrics(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ue_id: str
    cell_id: str
    rnti: str
    dl_throughput_mbps: float = Field(ge=0)
    ul_throughput_mbps: float = Field(ge=0)
    latency_ms: float = Field(ge=0)
    bler_pct: float = Field(ge=0, le=100)
    rsrp_dbm: float
    sinr_db: float
    qos_flow_id: int = Field(ge=1)


class RanSnapshot(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "oai-sim"
    cells: list[CellMetrics]
    ues: list[UeMetrics]


class RanAlert(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AlertSeverity
    entity: str
    metric: str
    value: float
    threshold: float
    message: str


@dataclass(frozen=True)
class Thresholds:
    max_latency_ms: float = 70.0
    max_packet_loss_pct: float = 2.0
    max_prb_utilization_pct: float = 90.0
    min_sinr_db: float = 5.0
    max_bler_pct: float = 10.0
    max_handover_failures: int = 3

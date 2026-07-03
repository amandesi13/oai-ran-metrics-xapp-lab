from __future__ import annotations

import math
import random
from datetime import datetime, timezone

from .models import CellMetrics, RanSnapshot, UeMetrics


class OaiRanSimulator:
    """Deterministic-enough OAI-style RAN KPI generator for demos and tests."""

    def __init__(self, seed: int = 42, gnb_id: str = "gNB-Dresden-01", cells: int = 2, ues_per_cell: int = 6) -> None:
        self.random = random.Random(seed)
        self.gnb_id = gnb_id
        self.cells = cells
        self.ues_per_cell = ues_per_cell
        self.tick = 0

    def snapshot(self, scenario: str = "normal") -> RanSnapshot:
        self.tick += 1
        now = datetime.now(timezone.utc)
        cell_metrics: list[CellMetrics] = []
        ue_metrics: list[UeMetrics] = []

        for cell_index in range(1, self.cells + 1):
            cell_id = f"cell-{cell_index}"
            load_wave = 48 + 18 * math.sin((self.tick + cell_index) / 5)
            jitter = self.random.uniform(-6, 6)
            dl_prb = clamp(load_wave + jitter, 8, 98)
            ul_prb = clamp(load_wave * 0.68 + self.random.uniform(-5, 5), 5, 95)
            latency = 22 + dl_prb * 0.28 + self.random.uniform(-4, 4)
            packet_loss = max(0.05, (dl_prb - 72) * 0.045 + self.random.uniform(0, 0.35))
            pusch_sinr = 17 - dl_prb * 0.06 + self.random.uniform(-1.5, 1.5)
            pucch_sinr = pusch_sinr - self.random.uniform(0.5, 2.5)
            handover_failures = 0 if dl_prb < 70 else self.random.randint(0, 2)

            if scenario == "congestion" and cell_index == 1:
                dl_prb = self.random.uniform(92, 98)
                ul_prb = self.random.uniform(80, 95)
                latency = self.random.uniform(85, 140)
                packet_loss = self.random.uniform(3.0, 8.0)
                handover_failures = self.random.randint(4, 8)
            elif scenario == "radio-degradation" and cell_index == 2:
                pusch_sinr = self.random.uniform(-2, 4)
                pucch_sinr = self.random.uniform(-4, 3)
                packet_loss = self.random.uniform(2.5, 6.0)

            active_ues = self.ues_per_cell + self.random.randint(-1, 2)
            avg_dl = max(1.0, 155 - dl_prb * 1.2 - packet_loss * 5)
            avg_ul = max(0.5, 42 - ul_prb * 0.25 - packet_loss * 2)

            cell_metrics.append(
                CellMetrics(
                    timestamp=now,
                    gnb_id=self.gnb_id,
                    cell_id=cell_id,
                    dl_prb_utilization=round(dl_prb, 2),
                    ul_prb_utilization=round(ul_prb, 2),
                    active_ues=active_ues,
                    avg_dl_throughput_mbps=round(avg_dl, 2),
                    avg_ul_throughput_mbps=round(avg_ul, 2),
                    avg_latency_ms=round(latency, 2),
                    packet_loss_pct=round(packet_loss, 2),
                    rrc_connected_ues=active_ues,
                    handover_failures=handover_failures,
                    pusch_sinr_db=round(pusch_sinr, 2),
                    pucch_sinr_db=round(pucch_sinr, 2),
                )
            )

            for ue_index in range(1, active_ues + 1):
                ue_id = f"ue-{cell_index}-{ue_index}"
                ue_sinr = pusch_sinr + self.random.uniform(-5, 4)
                bler = clamp((8 - ue_sinr) * 1.4 + packet_loss + self.random.uniform(0, 2), 0, 35)
                ue_metrics.append(
                    UeMetrics(
                        timestamp=now,
                        ue_id=ue_id,
                        cell_id=cell_id,
                        rnti=f"0x{cell_index:02x}{ue_index:02x}",
                        dl_throughput_mbps=round(max(0.5, avg_dl / max(active_ues, 1) + self.random.uniform(-2, 2)), 2),
                        ul_throughput_mbps=round(max(0.2, avg_ul / max(active_ues, 1) + self.random.uniform(-0.8, 0.8)), 2),
                        latency_ms=round(max(5, latency + self.random.uniform(-8, 12)), 2),
                        bler_pct=round(bler, 2),
                        rsrp_dbm=round(self.random.uniform(-112, -78), 2),
                        sinr_db=round(ue_sinr, 2),
                        qos_flow_id=self.random.choice([1, 5, 7, 9]),
                    )
                )

        return RanSnapshot(timestamp=now, cells=cell_metrics, ues=ue_metrics)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

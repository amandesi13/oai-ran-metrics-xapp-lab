from __future__ import annotations

from prometheus_client import CollectorRegistry, Gauge, generate_latest

from .models import RanAlert, RanSnapshot


class RanPrometheusExporter:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.dl_prb = Gauge("ran_cell_dl_prb_utilization_pct", "Downlink PRB utilization", ["cell_id"], registry=self.registry)
        self.ul_prb = Gauge("ran_cell_ul_prb_utilization_pct", "Uplink PRB utilization", ["cell_id"], registry=self.registry)
        self.latency = Gauge("ran_cell_avg_latency_ms", "Average cell latency", ["cell_id"], registry=self.registry)
        self.loss = Gauge("ran_cell_packet_loss_pct", "Packet loss", ["cell_id"], registry=self.registry)
        self.sinr = Gauge("ran_cell_pusch_sinr_db", "PUSCH SINR", ["cell_id"], registry=self.registry)
        self.ues = Gauge("ran_cell_active_ues", "Active UEs", ["cell_id"], registry=self.registry)
        self.alerts = Gauge("xapp_active_alerts", "Active xApp alerts", ["severity"], registry=self.registry)
        self.ue_bler = Gauge("ran_ue_bler_pct", "UE BLER", ["ue_id", "cell_id"], registry=self.registry)

    def update(self, snapshot: RanSnapshot, alerts: list[RanAlert]) -> None:
        for cell in snapshot.cells:
            self.dl_prb.labels(cell.cell_id).set(cell.dl_prb_utilization)
            self.ul_prb.labels(cell.cell_id).set(cell.ul_prb_utilization)
            self.latency.labels(cell.cell_id).set(cell.avg_latency_ms)
            self.loss.labels(cell.cell_id).set(cell.packet_loss_pct)
            self.sinr.labels(cell.cell_id).set(cell.pusch_sinr_db)
            self.ues.labels(cell.cell_id).set(cell.active_ues)

        for ue in snapshot.ues:
            self.ue_bler.labels(ue.ue_id, ue.cell_id).set(ue.bler_pct)

        by_severity = {"info": 0, "warning": 0, "critical": 0}
        for alert in alerts:
            by_severity[alert.severity.value] += 1
        for severity, count in by_severity.items():
            self.alerts.labels(severity).set(count)

    def render(self) -> bytes:
        return generate_latest(self.registry)

from __future__ import annotations

from .models import AlertSeverity, RanAlert, RanSnapshot, Thresholds


def detect_anomalies(snapshot: RanSnapshot, thresholds: Thresholds | None = None) -> list[RanAlert]:
    thresholds = thresholds or Thresholds()
    alerts: list[RanAlert] = []

    for cell in snapshot.cells:
        if cell.avg_latency_ms > thresholds.max_latency_ms:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.critical,
                    entity=cell.cell_id,
                    metric="avg_latency_ms",
                    value=cell.avg_latency_ms,
                    threshold=thresholds.max_latency_ms,
                    message=f"{cell.cell_id} latency is above threshold",
                )
            )
        if cell.packet_loss_pct > thresholds.max_packet_loss_pct:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.warning,
                    entity=cell.cell_id,
                    metric="packet_loss_pct",
                    value=cell.packet_loss_pct,
                    threshold=thresholds.max_packet_loss_pct,
                    message=f"{cell.cell_id} packet loss suggests congestion or radio degradation",
                )
            )
        if cell.dl_prb_utilization > thresholds.max_prb_utilization_pct:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.warning,
                    entity=cell.cell_id,
                    metric="dl_prb_utilization",
                    value=cell.dl_prb_utilization,
                    threshold=thresholds.max_prb_utilization_pct,
                    message=f"{cell.cell_id} downlink PRB utilization is near saturation",
                )
            )
        if min(cell.pusch_sinr_db, cell.pucch_sinr_db) < thresholds.min_sinr_db:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.warning,
                    entity=cell.cell_id,
                    metric="control_channel_sinr_db",
                    value=min(cell.pusch_sinr_db, cell.pucch_sinr_db),
                    threshold=thresholds.min_sinr_db,
                    message=f"{cell.cell_id} control/uplink channel SINR is weak",
                )
            )
        if cell.handover_failures > thresholds.max_handover_failures:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.warning,
                    entity=cell.cell_id,
                    metric="handover_failures",
                    value=float(cell.handover_failures),
                    threshold=float(thresholds.max_handover_failures),
                    message=f"{cell.cell_id} handover failures exceeded expected level",
                )
            )

    for ue in snapshot.ues:
        if ue.bler_pct > thresholds.max_bler_pct:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.info,
                    entity=ue.ue_id,
                    metric="bler_pct",
                    value=ue.bler_pct,
                    threshold=thresholds.max_bler_pct,
                    message=f"{ue.ue_id} BLER is elevated on {ue.cell_id}",
                )
            )
        if ue.sinr_db < thresholds.min_sinr_db:
            alerts.append(
                RanAlert(
                    severity=AlertSeverity.info,
                    entity=ue.ue_id,
                    metric="sinr_db",
                    value=ue.sinr_db,
                    threshold=thresholds.min_sinr_db,
                    message=f"{ue.ue_id} SINR is below target on {ue.cell_id}",
                )
            )

    return alerts

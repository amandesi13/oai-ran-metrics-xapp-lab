from oai_xapp_lab.detector import detect_anomalies
from oai_xapp_lab.prometheus_exporter import RanPrometheusExporter
from oai_xapp_lab.simulator import OaiRanSimulator


def test_exporter_renders_prometheus_metrics():
    snapshot = OaiRanSimulator(seed=4).snapshot("congestion")
    alerts = detect_anomalies(snapshot)
    exporter = RanPrometheusExporter()

    exporter.update(snapshot, alerts)
    metrics = exporter.render().decode("utf-8")

    assert "ran_cell_dl_prb_utilization_pct" in metrics
    assert "xapp_active_alerts" in metrics

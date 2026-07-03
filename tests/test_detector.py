from oai_xapp_lab.detector import detect_anomalies
from oai_xapp_lab.simulator import OaiRanSimulator


def test_normal_snapshot_has_fewer_alerts_than_congestion():
    normal_simulator = OaiRanSimulator(seed=7)
    congestion_simulator = OaiRanSimulator(seed=7)

    normal_alerts = detect_anomalies(normal_simulator.snapshot("normal"))
    congestion_alerts = detect_anomalies(congestion_simulator.snapshot("congestion"))

    assert len(congestion_alerts) > len(normal_alerts)
    assert any(alert.metric == "avg_latency_ms" for alert in congestion_alerts)


def test_radio_degradation_detects_low_sinr():
    simulator = OaiRanSimulator(seed=13)
    alerts = detect_anomalies(simulator.snapshot("radio-degradation"))

    assert any(alert.metric in {"control_channel_sinr_db", "sinr_db"} for alert in alerts)

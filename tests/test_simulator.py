from oai_xapp_lab.simulator import OaiRanSimulator


def test_simulator_emits_cells_and_ues():
    snapshot = OaiRanSimulator(seed=1, cells=2, ues_per_cell=4).snapshot()

    assert len(snapshot.cells) == 2
    assert len(snapshot.ues) >= 6
    assert snapshot.cells[0].gnb_id.startswith("gNB")

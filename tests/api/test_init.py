import json

def test_new_installation_writes_expected_config(tmp_path, monkeypatch):
    import merlin.api

    config_path = tmp_path / "config.json"

    # Redirect the module-level filename
    monkeypatch.setattr(merlin.api, "config_filename", str(config_path))

    merlin.api.new_installation(
        stream_name="/Test/Stream",
        num_phases=3,
        node="nodeA",
    )

    # Now inspect the actual file contents
    data = json.loads(config_path.read_text())

    assert data == {
        "node": "nodeA",
        "stream_name": "/Test/Stream",
        "num_phases": 3,
        "method": "unsupervised",
    }


def test_get_installation(monkeypatch):
    import merlin.api

    class FakeOfflineInstallation:
        def __init__(self, config_path):
            self.config_path = config_path

    monkeypatch.setattr(merlin.api, "OfflineInstallation",
                        FakeOfflineInstallation)

    inst = merlin.api.get_installation()

    assert isinstance(inst, FakeOfflineInstallation)
    assert inst.config_path == merlin.api.config_filename


def test_run_installation_constructs_realtime(monkeypatch):
    import merlin.api

    class FakeRealtime:
        def __init__(self, config_path, node):
            self.config_path = config_path
            self.node = node

    monkeypatch.setattr(merlin.api, "RealTimeInstallation", FakeRealtime)

    inst = merlin.api.run_installation("nodeA")

    assert isinstance(inst, FakeRealtime)
    assert inst.config_path == merlin.api.config_filename
    assert inst.node == "nodeA"

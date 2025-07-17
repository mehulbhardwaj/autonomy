import src


class DummyWM:
    def __init__(self, *a, **kw):
        self.kw = kw
        self.setup_called = False

    def setup_repository(self):
        self.setup_called = True


def test_create_workflow_manager(monkeypatch):
    monkeypatch.setattr(src, "WorkflowManager", DummyWM)
    mgr = src.create_workflow_manager("tok", "owner", "repo")
    assert isinstance(mgr, DummyWM)
    assert mgr.kw["config"].max_file_lines == 300


def test_quick_setup(monkeypatch):
    monkeypatch.setattr(
        src,
        "create_workflow_manager",
        lambda *a, **kw: DummyWM(),
    )
    mgr = src.quick_setup("tok", "owner", "repo")
    assert isinstance(mgr, DummyWM)
    assert mgr.setup_called

from pathlib import Path

from src.core.secret_vault import SecretVault
from src.slack.commands import SlashCommandHandler
from src.slack.mapping import SlackGitHubMapper


class DummyTM:
    def __init__(self):
        self.updated = None
        self.labels = None

    def get_next_task(self, assignee=None, team=None):
        assert assignee == "gh"
        return {"number": 1, "title": "task", "labels": ["priority-high"]}

    def update_task(self, issue_number, status=None, notes=None, done=False):
        self.updated = (issue_number, status, notes)
        return True

    def list_tasks(self, assignee=None, team=None, limit=10):
        assert assignee == "gh"
        return [
            {"number": 1, "title": "t1", "labels": ["in-progress"]},
            {"number": 2, "title": "t2", "labels": []},
        ]

    # methods for UndoManager
    def update_issue_labels(self, issue_number, add_labels=None, remove_labels=None):
        self.labels = (issue_number, add_labels, remove_labels)
        return True


def test_slack_github_mapper(tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    mapper = SlackGitHubMapper(vault)
    mapper.mapping_file = tmp_path / "m.json"
    mapper.set_mapping("U", "gh")
    assert mapper.get_github_user("U") == "gh"
    assert mapper.get_github_user("X") == "X"


def test_slash_next_with_mapping(tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    mapper = SlackGitHubMapper(vault)
    mapper.mapping_file = tmp_path / "m.json"
    mapper.set_mapping("U", "gh")
    handler = SlashCommandHandler(DummyTM(), mapper)
    resp = handler.handle_command("/autonomy next", {"user_id": "U"})
    assert resp["response_type"] == "ephemeral"
    assert "Next task" in resp["text"]
    assert resp["blocks"][0]["type"] == "section"


def test_slash_update_success(tmp_path):
    handler = SlashCommandHandler(DummyTM())
    resp = handler.handle_command("/autonomy update", {"text": "1", "user": "U"})
    assert "updated successfully" in resp["text"]


def test_slash_update_usage(tmp_path):
    handler = SlashCommandHandler(DummyTM())
    resp = handler.handle_command("/autonomy update", {"text": "abc"})
    assert "Usage" in resp["text"]


def test_slash_status(tmp_path):
    vault = SecretVault(vault_path=tmp_path / "v.json", key_path=tmp_path / "k.key")
    mapper = SlackGitHubMapper(vault)
    mapper.mapping_file = tmp_path / "m.json"
    mapper.set_mapping("U", "gh")
    handler = SlashCommandHandler(DummyTM(), mapper)
    resp = handler.handle_command("/autonomy status", {"user_id": "U"})
    assert resp["response_type"] == "ephemeral"
    assert resp["blocks"][1]["type"] == "fields"


def test_slash_undo(tmp_path: Path):
    from src.audit.logger import AuditLogger

    tm = DummyTM()
    tm.issue_manager = tm  # type: ignore[attr-defined]
    logger = AuditLogger(tmp_path / "audit.log")
    tm.audit_logger = logger

    h = logger.log(
        "update_labels", {"issue": 1, "add_labels": ["a"], "remove_labels": None}
    )
    handler = SlashCommandHandler(tm)
    resp = handler.handle_command("/autonomy undo", {"text": h})
    assert "Undo" in resp["text"]

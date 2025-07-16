from pathlib import Path

from src.github.board_manager import BoardManager


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._data


def test_init_board_creates_fields(tmp_path, monkeypatch):
    calls = []

    def dummy_post(url, headers=None, json=None, timeout=10):
        query = json["query"]
        calls.append(query)
        if "RepoProjects" in query:
            return DummyResponse(
                {"data": {"repository": {"id": "rid", "projectsV2": {"nodes": []}}}}
            )
        if "CreateProject" in query:
            return DummyResponse(
                {"data": {"createProjectV2": {"projectV2": {"id": "pid"}}}}
            )
        if "GetFields" in query:
            return DummyResponse({"data": {"node": {"fields": {"nodes": []}}}})
        if "CreateField" in query:
            return DummyResponse(
                {"data": {"createProjectV2Field": {"projectV2Field": {"id": "fid"}}}}
            )
        if "FieldOptions" in query:
            return DummyResponse({"data": {"node": {"options": {"nodes": []}}}})
        if "AddFieldOption" in query:
            return DummyResponse(
                {
                    "data": {
                        "addProjectV2FieldOption": {
                            "projectV2SingleSelectFieldOption": {"id": "oid"}
                        }
                    }
                }
            )
        return DummyResponse({"data": {}})

    monkeypatch.setattr("requests.post", dummy_post)
    cache = tmp_path / "cache.json"
    bm = BoardManager("t", "o", "r", cache_path=cache)
    result = bm.init_board()
    assert set(result) == {"Priority", "Pinned", "Sprint", "Track"}
    assert cache.exists()
    # ensure create project and field queries issued
    assert any("CreateProject" in q for q in calls)
    assert any("CreateField" in q for q in calls)


def test_init_board_uses_existing(tmp_path, monkeypatch):
    calls = []

    def dummy_post(url, headers=None, json=None, timeout=10):
        query = json["query"]
        calls.append(query)
        if "RepoProjects" in query:
            return DummyResponse(
                {
                    "data": {
                        "repository": {
                            "id": "rid",
                            "projectsV2": {
                                "nodes": [{"id": "pid", "title": "Autonomy Board"}]
                            },
                        }
                    }
                }
            )
        if "GetFields" in query:
            nodes = [
                {"id": f"id{i}", "name": name}
                for i, name in enumerate(["Priority", "Pinned", "Sprint", "Track"], 1)
            ]
            return DummyResponse({"data": {"node": {"fields": {"nodes": nodes}}}})
        if "FieldOptions" in query:
            opts = [
                {"name": opt}
                for opt in (
                    ["P0", "P1", "P2", "P3"]
                    if "id1" in json.get("variables", {}).get("fieldId", "")
                    else ["Yes", "No"]
                )
            ]
            return DummyResponse({"data": {"node": {"options": {"nodes": opts}}}})
        if "AddFieldOption" in query:
            raise AssertionError("Should not add options for existing fields")
        return DummyResponse({"data": {}})

    monkeypatch.setattr("requests.post", dummy_post)
    cache = tmp_path / "cache.json"
    bm = BoardManager("t", "o", "r", cache_path=cache)
    result = bm.init_board()
    assert set(result) == {"Priority", "Pinned", "Sprint", "Track"}
    assert cache.exists()

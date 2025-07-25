from src.github.board_manager import BoardManager


class DummyResponse:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self._data


def _mock_post_factory(items, record):
    def dummy_post(self, method, url, headers=None, json=None, timeout=10):
        query = json["query"]
        record.append(query)
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
        if "GetProjectItems" in query:
            return DummyResponse({"data": {"node": {"items": {"nodes": items}}}})
        if "updateProjectV2ItemPosition" in query:
            record.append(json["variables"])
            return DummyResponse(
                {
                    "data": {
                        "updateProjectV2ItemPosition": {
                            "projectV2Item": {"id": json["variables"]["itemId"]}
                        }
                    }
                }
            )
        return DummyResponse({"data": {}})

    return dummy_post


def test_rank_items(monkeypatch):
    items = [
        {
            "id": "it2",
            "fieldValues": {
                "nodes": [
                    {"field": {"name": "Priority"}, "name": "P0"},
                    {"field": {"name": "Pinned"}, "name": "No"},
                ]
            },
            "content": {
                "number": 2,
                "title": "B",
                "labels": {"nodes": []},
                "createdAt": "2025-07-15T00:00:00Z",
            },
        },
        {
            "id": "it1",
            "fieldValues": {
                "nodes": [
                    {"field": {"name": "Priority"}, "name": "P1"},
                    {"field": {"name": "Pinned"}, "name": "Yes"},
                ]
            },
            "content": {
                "number": 1,
                "title": "A",
                "labels": {"nodes": []},
                "createdAt": "2025-07-10T00:00:00Z",
            },
        },
    ]
    record = []
    monkeypatch.setattr(
        "src.github.client.ResilientGitHubClient.make_request",
        _mock_post_factory(items, record),
    )
    bm = BoardManager("t", "o", "r")
    ranked = bm.rank_items()
    assert [i["number"] for i in ranked] == [1, 2]


def test_reorder_items(monkeypatch):
    # Items initially [it2, it1] but ranking should be [it1, it2]
    items = [
        {
            "id": "it2",
            "fieldValues": {
                "nodes": [
                    {"field": {"name": "Priority"}, "name": "P0"},
                    {"field": {"name": "Pinned"}, "name": "No"},
                ]
            },
            "content": {
                "number": 2,
                "title": "B",
                "labels": {"nodes": []},
                "createdAt": "2025-07-15T00:00:00Z",
            },
        },
        {
            "id": "it1",
            "fieldValues": {
                "nodes": [
                    {"field": {"name": "Priority"}, "name": "P1"},
                    {"field": {"name": "Pinned"}, "name": "Yes"},
                ]
            },
            "content": {
                "number": 1,
                "title": "A",
                "labels": {"nodes": []},
                "createdAt": "2025-07-10T00:00:00Z",
            },
        },
    ]
    record = []
    monkeypatch.setattr(
        "src.github.client.ResilientGitHubClient.make_request",
        _mock_post_factory(items, record),
    )
    bm = BoardManager("t", "o", "r")
    bm.reorder_items()
    # ensure mutation called to move it2 after it1, but not for pinned item it1
    move_calls = [c for c in record if isinstance(c, dict)]
    assert any(call["itemId"] == "it2" for call in move_calls)
    assert not any(call.get("itemId") == "it1" for call in move_calls)

from src.core.platform import AutonomyPlatform, Mem0Client
from src.planning.workflow import PlanningWorkflow


def test_repository_isolation():
    mem = Mem0Client()
    mem.add({"k": "v1", "repository": "repo1"})
    mem.add({"k": "v2", "repository": "repo2"})
    assert mem.search("k", {"repository": "repo1"}) == "v1"
    assert mem.search("k", {"repository": "repo2"}) == "v2"


def test_memory_cleanup():
    mem = Mem0Client(max_entries=2)
    mem.add({"a": "1", "repository": "r"})
    mem.add({"b": "2", "repository": "r"})
    mem.add({"c": "3", "repository": "r"})
    repo_store = mem.store["r"]
    assert "a" not in repo_store and len(repo_store) == 2


def test_learn_from_override():
    platform = AutonomyPlatform()
    wf = platform.create_workflow(PlanningWorkflow)
    wf.learn_from_override("1", {"plan": "ai"}, {"plan": "human"}, repository="default")
    repo_store = platform.memory.store["default"]
    assert repo_store["ai_decision"] == "{'plan': 'ai'}"
    assert repo_store["human_decision"] == "{'plan': 'human'}"

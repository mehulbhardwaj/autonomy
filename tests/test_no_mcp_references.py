from pathlib import Path


def test_no_mcp_references():
    root = Path(__file__).resolve().parents[1]
    forbidden = ["autonomy-mcp", "Autonomy MCP"]
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for word in forbidden:
            assert word not in text, f"Found '{word}' in {path}"

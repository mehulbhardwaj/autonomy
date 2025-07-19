import json
from pathlib import Path
from typing import Dict, List


class PinnedItemsStore:
    """Simple file-based store for pinned items."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or Path.home() / ".autonomy"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.pinned_file = self.config_dir / "pinned_items.json"

    def load_pinned_items(self) -> Dict[str, List[str]]:
        if self.pinned_file.exists():
            with open(self.pinned_file, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except Exception:
                    return {}
        return {}

    def save_pinned_items(self, data: Dict[str, List[str]]) -> None:
        with open(self.pinned_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def pin_item(self, project_id: str, item_id: str) -> None:
        data = self.load_pinned_items()
        if project_id not in data:
            data[project_id] = []
        if item_id not in data[project_id]:
            data[project_id].append(item_id)
        self.save_pinned_items(data)

    def unpin_item(self, project_id: str, item_id: str) -> None:
        data = self.load_pinned_items()
        if project_id in data and item_id in data[project_id]:
            data[project_id].remove(item_id)
            if not data[project_id]:
                del data[project_id]
        self.save_pinned_items(data)

    def is_pinned(self, project_id: str, item_id: str) -> bool:
        data = self.load_pinned_items()
        return item_id in data.get(project_id, [])

    def list_pinned(self, project_id: str) -> List[str]:
        data = self.load_pinned_items()
        return data.get(project_id, [])

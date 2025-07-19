from pathlib import Path

from src.tasks.pinned_items import PinnedItemsStore


def test_pin_unpin(tmp_path: Path):
    store = PinnedItemsStore(config_dir=tmp_path)
    store.pin_item("proj", "1")
    assert store.is_pinned("proj", "1")
    store.unpin_item("proj", "1")
    assert not store.is_pinned("proj", "1")


def test_persistence(tmp_path: Path):
    store = PinnedItemsStore(config_dir=tmp_path)
    store.pin_item("proj", "1")
    new_store = PinnedItemsStore(config_dir=tmp_path)
    assert new_store.is_pinned("proj", "1")

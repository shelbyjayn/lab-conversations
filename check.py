"""Run a small database check: python check.py."""
from pathlib import Path
from tempfile import TemporaryDirectory
import database as db

with TemporaryDirectory() as folder:
    path = Path(folder) / "check.db"
    db.init_db(path)
    first = db.create_conversation(path, "Weekend plans")
    second = db.create_conversation(path, "Reading notes")
    db.add_message(path, first, "user", "Let's visit the library")
    db.add_message(path, first, "assistant", "It opens at ten")
    db.add_message(path, second, "user", "A library can also mean Python code")
    assert [r["id"] for r in db.list_conversations(path)] == [second, first]
    assert [r["role"] for r in db.get_messages(path, first)] == ["user", "assistant"]
    assert len(db.get_messages(path, second)) == 1
    results = db.search_messages(path, "LIBRARY")
    assert [r["title"] for r in results] == ["Weekend plans", "Reading notes"]
    assert db.search_messages(path, "not-in-any-message") == []
    db.init_db(path)
    assert len(db.list_conversations(path)) == 2
print("Database checks passed.")

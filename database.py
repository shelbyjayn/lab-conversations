"""Store conversations in SQLite. Complete the five unfinished functions below.

Rows returned to the app are dictionaries. With the supplied connection helper,
use dict(row) to turn one query result into a dictionary. get_conversation is a
working example you can use as a starting point.
"""
from contextlib import contextmanager
import sqlite3


@contextmanager
def connect(path):
    """Use with connect(path) as db to commit changes and close the connection."""
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def init_db(path):
    """Create the tables if needed; keep existing conversations."""
    with connect(path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                role TEXT NOT NULL,
                content TEXT NOT NULL
            );
        """)


def get_conversation(path, conversation_id):
    """Working example: return one conversation, or None if it doesn't exist."""
    with connect(path) as db:
        row = db.execute(
            "SELECT id, title FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def create_conversation(path, title):
    """Insert a conversation and return its integer id.

    SQLite assigns the id. The cursor returned by execute has a lastrowid
    attribute. Save the change so it survives closing the program.
    """
    raise NotImplementedError("Complete create_conversation")


def list_conversations(path):
    """Return all conversations, newest first (descending id).

    Each item is a dictionary with keys id and title. Return [] when empty.
    """
    raise NotImplementedError("Complete list_conversations")


def add_message(path, conversation_id, role, content):
    """Insert a message and return its integer id.

    conversation_id refers to an existing conversation; role is either 'user'
    or 'assistant'. Store content exactly as given, including quotes/newlines.
    """
    raise NotImplementedError("Complete add_message")


def get_messages(path, conversation_id):
    """Return this conversation's messages in sending order (ascending id).

    Each dictionary has keys id, conversation_id, role, and content.
    Return [] when there are no messages for that conversation.
    """
    raise NotImplementedError("Complete get_messages")


def search_messages(path, term):
    """Find messages whose content contains term, using SQL LIKE.

    Join conversations to messages. Each result is a dictionary with keys
    id (the message id), title, role, and content, ordered by ascending message id.
    Match ASCII letters without regard to case. An empty term matches every
    message. LIKE's % and _ wildcards keep their usual meaning.
    """
    raise NotImplementedError("Complete search_messages")

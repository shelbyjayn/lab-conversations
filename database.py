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
    with connect(path) as db:
        cursor = db.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,),
        )
        return cursor.lastrowid


def list_conversations(path):
    """Return all conversations, newest first (descending id).

    Each item is a dictionary with keys id and title. Return [] when empty.
    """
    with connect(path) as db:
        rows = db.execute(
            "SELECT id, title FROM conversations ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def add_message(path, conversation_id, role, content):
    """Insert a message and return its integer id.

    conversation_id refers to an existing conversation; role is either 'user'
    or 'assistant'. Store content exactly as given, including quotes/newlines.
    """
    with connect(path) as db:
        cursor = db.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )
        return cursor.lastrowid


def get_messages(path, conversation_id):
    """Return this conversation's messages in sending order (ascending id).

    Each dictionary has keys id, conversation_id, role, and content.
    Return [] when there are no messages for that conversation.
    """
    with connect(path) as db:
        rows = db.execute(
            "SELECT id, conversation_id, role, content FROM messages "
            "WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def search_messages(path, term):
    """Find messages whose content contains term, using SQL LIKE.

    Join conversations to messages. Each result is a dictionary with keys
    id (the message id), title, role, and content, ordered by ascending message id.
    Match ASCII letters without regard to case. An empty term matches every
    message. LIKE's % and _ wildcards keep their usual meaning.
    """
    pattern = "%" + term + "%"
    with connect(path) as db:
        rows = db.execute(
            "SELECT messages.id, conversations.title, messages.role, messages.content "
            "FROM messages "
            "JOIN conversations ON messages.conversation_id = conversations.id "
            "WHERE messages.content LIKE ? "
            "ORDER BY messages.id ASC",
            (pattern,),
        ).fetchall()
        return [dict(row) for row in rows]
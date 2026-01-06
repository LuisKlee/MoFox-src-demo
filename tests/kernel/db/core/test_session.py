import pytest
from sqlalchemy import text

from kernel.db.core.session import SessionManager


def test_session_scope_commits_and_rolls_back(sqlite_engine):
    with sqlite_engine.connect() as conn:
        conn.execute(text("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)"))
        conn.commit()

    session_manager = SessionManager(sqlite_engine)

    with session_manager.session_scope() as session:
        session.execute(text("INSERT INTO notes (body) VALUES (:body)"), {"body": "hello"})

    with session_manager.session_scope() as session:
        values = session.execute(text("SELECT body FROM notes ORDER BY id"))
        bodies = values.scalars().all()
    assert bodies == ["hello"]

    with pytest.raises(RuntimeError):
        with session_manager.session_scope() as session:
            session.execute(text("INSERT INTO notes (body) VALUES (:body)"), {"body": "fail"})
            raise RuntimeError("force rollback")

    with session_manager.session_scope() as session:
        values = session.execute(text("SELECT body FROM notes ORDER BY id"))
        bodies = values.scalars().all()
    assert bodies == ["hello"]

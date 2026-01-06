from sqlalchemy import text


def test_engine_executes_basic_sql(sqlite_engine):
    with sqlite_engine.connect() as conn:
        conn.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"))
        conn.execute(text("INSERT INTO items (name) VALUES (:name)"), [
            {"name": "apple"},
            {"name": "banana"},
        ])
        conn.commit()

        rows = conn.execute(text("SELECT name FROM items ORDER BY id"))
        names = rows.scalars().all()

    assert names == ["apple", "banana"]

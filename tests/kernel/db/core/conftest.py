from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MOFOX_SRC_PATH = PROJECT_ROOT / "src"
if str(MOFOX_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(MOFOX_SRC_PATH))

from kernel.db.core.dialect_adapter import EngineConfig
from kernel.db.core.engine import EngineManager


@pytest.fixture
def sqlite_engine(tmp_path):
    """Provide a SQLite engine backed by a temporary file."""

    db_path = tmp_path / "test.db"
    manager = EngineManager()
    engine = manager.create(EngineConfig(dialect="sqlite", database=str(db_path)))
    try:
        yield engine
    finally:
        engine.dispose()

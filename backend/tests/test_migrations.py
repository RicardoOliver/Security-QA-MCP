import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_expected_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "test_migrations.sqlite"
    db_url = f"sqlite:///{db_path}"
    backend_dir = Path(__file__).resolve().parent.parent

    os.environ["DATABASE_URL"] = db_url

    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert {"users", "findings", "scans"}.issubset(tables)

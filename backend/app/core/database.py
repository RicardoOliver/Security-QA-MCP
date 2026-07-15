import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine_kwargs = {"future": True}
if settings.database_url.startswith("sqlite"):
    engine_kwargs.update(
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    )

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.domain.models import environment, finding, permission, project, role, role_permission, scan, target, tenant, user  # noqa: F401

    Base.metadata.create_all(bind=engine)

    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///./", "")
        path = Path(db_path).resolve()
        if path.exists():
            with sqlite3.connect(path) as connection:
                findings_columns = connection.execute("PRAGMA table_info(findings)").fetchall()
                if not any(column[1] == "scan_id" for column in findings_columns):
                    connection.execute("ALTER TABLE findings ADD COLUMN scan_id INTEGER")

                scans_columns = connection.execute("PRAGMA table_info(scans)").fetchall()
                for column_name in ["created_at", "updated_at", "findings_count"]:
                    if not any(column[1] == column_name for column in scans_columns):
                        connection.execute(f"ALTER TABLE scans ADD COLUMN {column_name} INTEGER")
                connection.commit()


init_db()

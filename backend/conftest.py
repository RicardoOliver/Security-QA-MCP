import os
import pytest
from sqlalchemy import text

from app.core.database import SessionLocal, engine, init_db
from app.domain.models.finding import Finding
from app.domain.models.user import User


@pytest.fixture(autouse=True)
def reset_database():
    init_db()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM findings"))
        conn.execute(text("DELETE FROM users"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM findings"))
        conn.execute(text("DELETE FROM users"))

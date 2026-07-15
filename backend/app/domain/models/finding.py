from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    scan_id: Mapped[int | None] = mapped_column(ForeignKey("scans.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="medium")
    description: Mapped[str] = mapped_column(Text, default="")

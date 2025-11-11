"""SQLAlchemy models for profiles module."""

from sqlalchemy import ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column

from src.core.infrastructure.database import Base

# Follow association table (many-to-many self-referential relationship)
follow_association = Table(
    "follows",
    Base.metadata,
    mapped_column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    mapped_column("followee_id", Integer, ForeignKey("users.id"), primary_key=True),
)

"""SQLAlchemy models for profiles module."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.infrastructure.database import Base

# Follow association table (many-to-many self-referential relationship)
follow_association = Table(
    "follows",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("followee_id", Integer, ForeignKey("users.id"), primary_key=True),
)

"""SQLAlchemy models for auth module."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base

if TYPE_CHECKING:
    from src.modules.articles.infrastructure.models import ArticleModel


class UserModel(Base):
    """SQLAlchemy model for User entity."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    articles: Mapped[list["ArticleModel"]] = relationship(
        "ArticleModel", back_populates="author", lazy="selectin"
    )
    favorited_articles: Mapped[list["ArticleModel"]] = relationship(
        "ArticleModel",
        secondary="article_favorites",
        back_populates="favorited_by",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"UserModel(id={self.id}, email={self.email}, name={self.name})"

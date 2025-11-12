"""SQLAlchemy models for articles module."""

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.infrastructure.database import Base


# Association table for article tags
article_tag_association = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_name", String(50), ForeignKey("tags.name"), primary_key=True),
)

# Association table for article favorites
article_favorite_association = Table(
    "article_favorites",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class TagModel(Base):
    """SQLAlchemy model for tags."""

    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Relationships
    articles: Mapped[list["ArticleModel"]] = relationship(
        "ArticleModel",
        secondary=article_tag_association,
        back_populates="tags",
    )


class ArticleModel(Base):
    """SQLAlchemy model for articles."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    author: Mapped["UserModel"] = relationship("UserModel", back_populates="articles")  # type: ignore
    tags: Mapped[list[TagModel]] = relationship(
        TagModel,
        secondary=article_tag_association,
        back_populates="articles",
    )
    favorited_by: Mapped[list["UserModel"]] = relationship(  # type: ignore
        "UserModel",
        secondary=article_favorite_association,
        back_populates="favorited_articles",
    )

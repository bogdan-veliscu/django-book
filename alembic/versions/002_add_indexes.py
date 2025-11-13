"""Add database indexes for performance optimization.

Revision ID: 002_add_indexes
Revises: 001_initial
Create Date: 2024-11-13 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_indexes"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes."""
    # Articles table indexes
    # Note: articles.slug already has unique index from initial migration
    op.create_index(
        "ix_articles_author_id",
        "articles",
        ["author_id"],
        unique=False,
    )
    op.create_index(
        "ix_articles_created_at",
        "articles",
        ["created_at"],
        unique=False,
        postgresql_ops={"created_at": "DESC"},
    )

    # Users table indexes
    # Note: users.email already has unique index from initial migration
    op.create_index(
        "ix_users_name",
        "users",
        ["name"],
        unique=False,
    )

    # Comments table indexes
    op.create_index(
        "ix_comments_article_id",
        "comments",
        ["article_id"],
        unique=False,
    )
    op.create_index(
        "ix_comments_author_id",
        "comments",
        ["author_id"],
        unique=False,
    )
    op.create_index(
        "ix_comments_created_at",
        "comments",
        ["created_at"],
        unique=False,
        postgresql_ops={"created_at": "DESC"},
    )

    # Composite index for article filtering queries
    op.create_index(
        "ix_articles_author_created",
        "articles",
        ["author_id", "created_at"],
        unique=False,
        postgresql_ops={"created_at": "DESC"},
    )


def downgrade() -> None:
    """Remove performance indexes."""
    # Drop composite index
    op.drop_index("ix_articles_author_created", table_name="articles")

    # Drop comments indexes
    op.drop_index("ix_comments_created_at", table_name="comments")
    op.drop_index("ix_comments_author_id", table_name="comments")
    op.drop_index("ix_comments_article_id", table_name="comments")

    # Drop users indexes
    op.drop_index("ix_users_name", table_name="users")

    # Drop articles indexes
    op.drop_index("ix_articles_created_at", table_name="articles")
    op.drop_index("ix_articles_author_id", table_name="articles")

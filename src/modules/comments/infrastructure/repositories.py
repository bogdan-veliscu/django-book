"""Comment repository implementations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.comments.domain.entities import Comment
from src.modules.comments.domain.repositories import ICommentRepository
from src.modules.comments.infrastructure.models import CommentModel


class CommentRepository(ICommentRepository):
    """SQLAlchemy implementation of comment repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: The database session.
        """
        self._session = session

    def _model_to_entity(self, model: CommentModel) -> Comment:
        """Convert CommentModel to Comment entity.

        Args:
            model: The SQLAlchemy model.

        Returns:
            The domain entity.
        """
        return Comment(
            id=model.id,
            body=model.body,
            author_id=model.author_id,
            article_id=model.article_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(
        self, entity: Comment, model: CommentModel | None = None
    ) -> CommentModel:
        """Convert Comment entity to CommentModel.

        Args:
            entity: The domain entity.
            model: Optional existing model to update.

        Returns:
            The SQLAlchemy model.
        """
        if model is None:
            model = CommentModel()

        model.body = entity.body
        model.author_id = entity.author_id
        model.article_id = entity.article_id
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        return model

    async def add(self, entity: Comment) -> Comment:
        """Add a new comment.

        Args:
            entity: The comment to add.

        Returns:
            The added comment with ID.
        """
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def get(self, id: int) -> Comment | None:
        """Get a comment by ID.

        Args:
            id: The comment ID.

        Returns:
            The comment if found, None otherwise.
        """
        stmt = select(CommentModel).where(CommentModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def update(self, entity: Comment) -> Comment:
        """Update a comment.

        Args:
            entity: The comment to update.

        Returns:
            The updated comment.
        """
        stmt = select(CommentModel).where(CommentModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Comment with id {entity.id} not found")

        model.body = entity.body
        model.updated_at = entity.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def delete(self, id: int) -> None:
        """Delete a comment.

        Args:
            id: The comment ID.
        """
        stmt = select(CommentModel).where(CommentModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_by_article(
        self, article_id: int, limit: int = 20, offset: int = 0
    ) -> list[Comment]:
        """List comments for an article.

        Args:
            article_id: The article's ID.
            limit: Maximum number of comments to return.
            offset: Number of comments to skip.

        Returns:
            List of comments ordered by creation date (newest first).
        """
        stmt = (
            select(CommentModel)
            .where(CommentModel.article_id == article_id)
            .order_by(CommentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def list_by_author(
        self, author_id: int, limit: int = 20, offset: int = 0
    ) -> list[Comment]:
        """List comments by author.

        Args:
            author_id: The author's user ID.
            limit: Maximum number of comments to return.
            offset: Number of comments to skip.

        Returns:
            List of comments ordered by creation date (newest first).
        """
        stmt = (
            select(CommentModel)
            .where(CommentModel.author_id == author_id)
            .order_by(CommentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def count_by_article(self, article_id: int) -> int:
        """Count comments for an article.

        Args:
            article_id: The article's ID.

        Returns:
            Number of comments on the article.
        """
        stmt = select(func.count(CommentModel.id)).where(
            CommentModel.article_id == article_id
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()

        return count

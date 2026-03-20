"""Article repository implementations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.articles.domain.entities import Article, Tag
from src.modules.articles.domain.repositories import IArticleRepository, ITagRepository
from src.modules.articles.domain.value_objects import Slug
from src.modules.articles.infrastructure.models import (
    ArticleModel,
    TagModel,
    article_favorite_association,
)
from src.modules.profiles.infrastructure.models import follow_association


class ArticleRepository(IArticleRepository):
    """SQLAlchemy implementation of article repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: The database session.
        """
        self._session = session

    def _model_to_entity(self, model: ArticleModel) -> Article:
        """Convert ArticleModel to Article entity.

        Args:
            model: The SQLAlchemy model.

        Returns:
            The domain entity.
        """
        return Article(
            id=model.id,
            title=model.title,
            description=model.description,
            body=model.body,
            author_id=model.author_id,
            slug=Slug(model.slug),
            tags={tag.name for tag in model.tags},
            favorites={user.id for user in model.favorited_by},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Article, model: ArticleModel | None = None) -> ArticleModel:
        """Convert Article entity to ArticleModel.

        Args:
            entity: The domain entity.
            model: Optional existing model to update.

        Returns:
            The SQLAlchemy model.
        """
        if model is None:
            model = ArticleModel()

        model.title = entity.title
        model.description = entity.description
        model.body = entity.body
        model.author_id = entity.author_id
        model.slug = entity.slug.value
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at

        return model

    async def add(self, entity: Article) -> Article:
        """Add a new article.

        Args:
            entity: The article to add.

        Returns:
            The added article with ID.
        """
        model = self._entity_to_model(entity)

        # Handle tags
        tag_models = []
        for tag_name in entity.tags:
            # Get or create tag
            stmt = select(TagModel).where(TagModel.name == tag_name)
            result = await self._session.execute(stmt)
            tag_model = result.scalar_one_or_none()

            if tag_model is None:
                tag_model = TagModel(name=tag_name)
                self._session.add(tag_model)

            tag_models.append(tag_model)

        model.tags = tag_models

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["tags", "favorited_by"])

        return self._model_to_entity(model)

    async def get(self, id: int) -> Article | None:
        """Get an article by ID.

        Args:
            id: The article ID.

        Returns:
            The article if found, None otherwise.
        """
        stmt = (
            select(ArticleModel)
            .where(ArticleModel.id == id)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Article | None:
        """Get an article by slug.

        Args:
            slug: The article's slug.

        Returns:
            The article if found, None otherwise.
        """
        stmt = (
            select(ArticleModel)
            .where(ArticleModel.slug == slug)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def update(self, entity: Article) -> Article:
        """Update an article.

        Args:
            entity: The article to update.

        Returns:
            The updated article.
        """
        stmt = (
            select(ArticleModel)
            .where(ArticleModel.id == entity.id)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Article with id {entity.id} not found")

        # Update basic fields
        model.title = entity.title
        model.description = entity.description
        model.body = entity.body
        model.slug = entity.slug.value
        model.updated_at = entity.updated_at

        # Update tags
        tag_models = []
        for tag_name in entity.tags:
            # Get or create tag
            tag_stmt = select(TagModel).where(TagModel.name == tag_name)
            tag_result = await self._session.execute(tag_stmt)
            tag_model = tag_result.scalar_one_or_none()

            if tag_model is None:
                tag_model = TagModel(name=tag_name)
                self._session.add(tag_model)
                await self._session.flush()

            tag_models.append(tag_model)

        model.tags = tag_models

        # Update favorites
        # Get user models for favorited_by
        from src.modules.auth.infrastructure.models import UserModel

        favorited_user_ids = list(entity.favorites)
        if favorited_user_ids:
            users_stmt = select(UserModel).where(UserModel.id.in_(favorited_user_ids))
            users_result = await self._session.execute(users_stmt)
            user_models = list(users_result.scalars())
            model.favorited_by = user_models
        else:
            model.favorited_by = []

        await self._session.flush()
        await self._session.refresh(model, ["tags", "favorited_by"])

        return self._model_to_entity(model)

    async def delete(self, id: int) -> None:
        """Delete an article.

        Args:
            id: The article ID.
        """
        stmt = select(ArticleModel).where(ArticleModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_by_author(
        self, author_id: int, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List articles by author.

        Args:
            author_id: The author's user ID.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        stmt = (
            select(ArticleModel)
            .where(ArticleModel.author_id == author_id)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
            .order_by(ArticleModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def list_by_tag(
        self, tag: str, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List articles by tag.

        Args:
            tag: The tag name.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        stmt = (
            select(ArticleModel)
            .join(ArticleModel.tags)
            .where(TagModel.name == tag.lower())
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
            .order_by(ArticleModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def list_favorited_by(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List articles favorited by a user.

        Args:
            user_id: The user's ID.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        stmt = (
            select(ArticleModel)
            .join(article_favorite_association)
            .where(article_favorite_association.c.user_id == user_id)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
            .order_by(ArticleModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def get_feed(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """Get article feed for a user (from followed authors).

        Args:
            user_id: The user's ID.
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles from followed authors.
        """
        # Get articles from authors that the user follows
        stmt = (
            select(ArticleModel)
            .join(
                follow_association,
                ArticleModel.author_id == follow_association.c.followee_id,
            )
            .where(follow_association.c.follower_id == user_id)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
            .order_by(ArticleModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def list_all(
        self, limit: int = 20, offset: int = 0
    ) -> list[Article]:
        """List all articles.

        Args:
            limit: Maximum number of articles to return.
            offset: Number of articles to skip.

        Returns:
            List of articles.
        """
        stmt = (
            select(ArticleModel)
            .options(selectinload(ArticleModel.tags), selectinload(ArticleModel.favorited_by))
            .order_by(ArticleModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def get_all_tags(self) -> list[str]:
        """Get all unique tags used in articles.

        Returns:
            List of tag names.
        """
        stmt = select(TagModel.name).order_by(TagModel.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class TagRepository(ITagRepository):
    """SQLAlchemy implementation of tag repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: The database session.
        """
        self._session = session

    def _model_to_entity(self, model: TagModel) -> Tag:
        """Convert TagModel to Tag entity.

        Args:
            model: The SQLAlchemy model.

        Returns:
            The domain entity.
        """
        return Tag(name=model.name)

    async def add(self, entity: Tag) -> Tag:
        """Add a new tag.

        Args:
            entity: The tag to add.

        Returns:
            The added tag.
        """
        model = TagModel(name=entity.name)
        self._session.add(model)
        await self._session.flush()

        return self._model_to_entity(model)

    async def get(self, id: int) -> Tag | None:
        """Get a tag by ID.

        Args:
            id: The tag ID.

        Returns:
            The tag if found, None otherwise.
        """
        # Tags use name as primary key, so this method doesn't apply
        raise NotImplementedError("Tags use name as primary key")

    async def get_by_name(self, name: str) -> Tag | None:
        """Get a tag by name.

        Args:
            name: The tag name.

        Returns:
            The tag if found, None otherwise.
        """
        stmt = select(TagModel).where(TagModel.name == name.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def get_or_create(self, name: str) -> Tag:
        """Get a tag by name or create it if it doesn't exist.

        Args:
            name: The tag name.

        Returns:
            The tag (existing or newly created).
        """
        tag = await self.get_by_name(name)
        if tag is None:
            tag = Tag(name=name)
            tag = await self.add(tag)

        return tag

    async def update(self, entity: Tag) -> Tag:
        """Update a tag.

        Args:
            entity: The tag to update.

        Returns:
            The updated tag.
        """
        # Tags are immutable (only have a name), so no update needed
        return entity

    async def delete(self, id: int) -> None:
        """Delete a tag.

        Args:
            id: The tag ID.
        """
        # Tags use name as primary key, so this method doesn't apply
        raise NotImplementedError("Tags use name as primary key")

"""FastAPI routes for articles module."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.core.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.core.infrastructure.database import get_db_session
from src.modules.articles.application.commands.create_article import CreateArticle
from src.modules.articles.application.commands.delete_article import DeleteArticle
from src.modules.articles.application.commands.favorite_article import FavoriteArticle
from src.modules.articles.application.commands.unfavorite_article import (
    UnfavoriteArticle,
)
from src.modules.articles.application.commands.update_article import UpdateArticle
from src.modules.articles.application.dtos import (
    ArticleDTO,
    CreateArticleRequest,
    UpdateArticleRequest,
)
from src.modules.articles.application.queries.get_article import GetArticle
from src.modules.articles.infrastructure.repositories import ArticleRepository
from src.modules.articles.presentation.schemas import (
    ArticleResponseSchema,
    ArticleSchema,
    CreateArticleSchema,
    MultipleArticlesResponseSchema,
    ProfileSchema,
    TagsResponseSchema,
    UpdateArticleSchema,
)
from src.modules.auth.infrastructure.repositories import UserRepository
from src.modules.auth.presentation.dependencies import get_current_user, get_optional_user
from src.modules.profiles.infrastructure.repositories import ProfileRepository

router = APIRouter(prefix="/articles", tags=["articles"])


def _article_dto_to_schema(article: ArticleDTO, following: bool = False) -> ArticleSchema:
    """Convert ArticleDTO to ArticleSchema.

    Args:
        article: The article DTO.
        following: Whether the current user is following the author.

    Returns:
        The article schema.
    """
    return ArticleSchema(
        slug=article.slug,
        title=article.title,
        description=article.description,
        body=article.body,
        tagList=article.tags,
        createdAt=article.created_at,
        updatedAt=article.updated_at,
        favorited=article.favorited,
        favoritesCount=article.favorites_count,
        author=ProfileSchema(
            username=article.author.name,
            bio=article.author.bio,
            image=article.author.image,
            following=following,
        ),
    )


@router.post("", response_model=ArticleResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_article(
    request: CreateArticleSchema,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> ArticleResponseSchema:
    """Create a new article.

    Args:
        request: The create article request.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        The created article.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    use_case = CreateArticle(article_repo)

    try:
        article_dto = await use_case.execute(
            CreateArticleRequest(
                title=request.article.title,
                description=request.article.description,
                body=request.article.body,
                tags=request.article.tagList,
                author_id=current_user["id"],
            )
        )

        # Get author details
        author = await user_repo.get(article_dto.author.name if hasattr(article_dto.author, "name") else current_user["id"])
        if author:
            article_dto.author.name = author.name
            article_dto.author.bio = author.bio
            article_dto.author.image = author.image

        # Check if following (always False for own articles)
        following = False

        article_schema = _article_dto_to_schema(article_dto, following)
        return ArticleResponseSchema(article=article_schema)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{slug}", response_model=ArticleResponseSchema)
async def get_article(
    slug: str,
    current_user: dict | None = Depends(get_optional_user),
    session=Depends(get_db_session),
) -> ArticleResponseSchema:
    """Get an article by slug.

    Args:
        slug: The article slug.
        current_user: The authenticated user (optional).
        session: Database session.

    Returns:
        The article.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    use_case = GetArticle(article_repo, user_repo)

    try:
        current_user_id = current_user["id"] if current_user else None
        article_dto = await use_case.execute(slug, current_user_id)

        # Check if following
        following = False
        if current_user_id:
            profile = await profile_repo.get_by_user_id(article_dto.author.name)  # This needs fixing
            if profile:
                following = profile.is_following(current_user_id)

        article_schema = _article_dto_to_schema(article_dto, following)
        return ArticleResponseSchema(article=article_schema)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{slug}", response_model=ArticleResponseSchema)
async def update_article(
    slug: str,
    request: UpdateArticleSchema,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> ArticleResponseSchema:
    """Update an article.

    Args:
        slug: The article slug.
        request: The update article request.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        The updated article.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    use_case = UpdateArticle(article_repo)

    try:
        article_dto = await use_case.execute(
            slug,
            current_user["id"],
            UpdateArticleRequest(
                title=request.article.title,
                description=request.article.description,
                body=request.article.body,
            ),
        )

        # Get author details
        author = await user_repo.get(current_user["id"])
        if author:
            article_dto.author.name = author.name
            article_dto.author.bio = author.bio
            article_dto.author.image = author.image

        # Check if following (always False for own articles)
        following = False

        article_schema = _article_dto_to_schema(article_dto, following)
        return ArticleResponseSchema(article=article_schema)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    slug: str,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> None:
    """Delete an article.

    Args:
        slug: The article slug.
        current_user: The authenticated user.
        session: Database session.
    """
    article_repo = ArticleRepository(session)

    use_case = DeleteArticle(article_repo)

    try:
        await use_case.execute(slug, current_user["id"])
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{slug}/favorite", response_model=ArticleResponseSchema)
async def favorite_article(
    slug: str,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> ArticleResponseSchema:
    """Favorite an article.

    Args:
        slug: The article slug.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        The favorited article.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    use_case = FavoriteArticle(article_repo, user_repo)

    try:
        article_dto = await use_case.execute(slug, current_user["id"])

        # Check if following
        following = False
        profile = await profile_repo.get_by_user_id(article_dto.author.name)  # This needs fixing
        if profile:
            following = profile.is_following(current_user["id"])

        article_schema = _article_dto_to_schema(article_dto, following)
        return ArticleResponseSchema(article=article_schema)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{slug}/favorite", response_model=ArticleResponseSchema)
async def unfavorite_article(
    slug: str,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> ArticleResponseSchema:
    """Unfavorite an article.

    Args:
        slug: The article slug.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        The unfavorited article.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    use_case = UnfavoriteArticle(article_repo, user_repo)

    try:
        article_dto = await use_case.execute(slug, current_user["id"])

        # Check if following
        following = False
        profile = await profile_repo.get_by_user_id(article_dto.author.name)  # This needs fixing
        if profile:
            following = profile.is_following(current_user["id"])

        article_schema = _article_dto_to_schema(article_dto, following)
        return ArticleResponseSchema(article=article_schema)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=MultipleArticlesResponseSchema)
async def list_articles(
    tag: str | None = Query(None),
    author: str | None = Query(None),
    favorited: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict | None = Depends(get_optional_user),
    session=Depends(get_db_session),
) -> MultipleArticlesResponseSchema:
    """List articles with filters.

    Args:
        tag: Filter by tag.
        author: Filter by author username.
        favorited: Filter by user who favorited.
        limit: Maximum number of articles.
        offset: Number of articles to skip.
        current_user: The authenticated user (optional).
        session: Database session.

    Returns:
        List of articles.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    articles: list[ArticleDTO] = []

    # Apply filters
    if tag:
        article_entities = await article_repo.list_by_tag(tag, limit, offset)
    elif author:
        # Get author by username
        author_user = await user_repo.get_by_email(author)  # This needs fixing - should be by username
        if author_user:
            article_entities = await article_repo.list_by_author(
                author_user.id, limit, offset  # type: ignore
            )
        else:
            article_entities = []
    elif favorited:
        # Get user by username
        favorited_user = await user_repo.get_by_email(favorited)  # This needs fixing
        if favorited_user:
            article_entities = await article_repo.list_favorited_by(
                favorited_user.id, limit, offset  # type: ignore
            )
        else:
            article_entities = []
    else:
        # Get all articles (we'll need to add this method)
        article_entities = []

    # Convert to DTOs
    current_user_id = current_user["id"] if current_user else None

    for article_entity in article_entities:
        # Get author
        author_user = await user_repo.get(article_entity.author_id)
        if not author_user:
            continue

        # Check if favorited
        favorited_by_current = False
        if current_user_id:
            favorited_by_current = article_entity.is_favorited_by(current_user_id)

        # Check if following
        following = False
        if current_user_id:
            profile = await profile_repo.get_by_user_id(author_user.id)  # type: ignore
            if profile:
                following = profile.is_following(current_user_id)

        article_dto = ArticleDTO(
            id=article_entity.id,  # type: ignore
            slug=article_entity.slug.value,
            title=article_entity.title,
            description=article_entity.description,
            body=article_entity.body,
            tags=list(article_entity.tags),
            created_at=article_entity.created_at,
            updated_at=article_entity.updated_at,
            favorited=favorited_by_current,
            favorites_count=article_entity.favorites_count(),
            author=ProfileSchema(
                username=author_user.name,
                bio=author_user.bio,
                image=author_user.image,
                following=following,
            ),
        )
        articles.append(article_dto)

    article_schemas = [_article_dto_to_schema(article, False) for article in articles]
    return MultipleArticlesResponseSchema(
        articles=article_schemas, articlesCount=len(article_schemas)
    )


@router.get("/feed", response_model=MultipleArticlesResponseSchema)
async def get_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> MultipleArticlesResponseSchema:
    """Get article feed for current user.

    Args:
        limit: Maximum number of articles.
        offset: Number of articles to skip.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        List of articles from followed authors.
    """
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    article_entities = await article_repo.get_feed(current_user["id"], limit, offset)

    articles: list[ArticleDTO] = []

    for article_entity in article_entities:
        # Get author
        author_user = await user_repo.get(article_entity.author_id)
        if not author_user:
            continue

        # Check if favorited
        favorited_by_current = article_entity.is_favorited_by(current_user["id"])

        # Following is always True for feed
        following = True

        article_dto = ArticleDTO(
            id=article_entity.id,  # type: ignore
            slug=article_entity.slug.value,
            title=article_entity.title,
            description=article_entity.description,
            body=article_entity.body,
            tags=list(article_entity.tags),
            created_at=article_entity.created_at,
            updated_at=article_entity.updated_at,
            favorited=favorited_by_current,
            favorites_count=article_entity.favorites_count(),
            author=ProfileSchema(
                username=author_user.name,
                bio=author_user.bio,
                image=author_user.image,
                following=following,
            ),
        )
        articles.append(article_dto)

    article_schemas = [_article_dto_to_schema(article, True) for article in articles]
    return MultipleArticlesResponseSchema(
        articles=article_schemas, articlesCount=len(article_schemas)
    )


# Separate tags router
tags_router = APIRouter(prefix="/tags", tags=["tags"])


@tags_router.get("", response_model=TagsResponseSchema)
async def get_tags(session=Depends(get_db_session)) -> TagsResponseSchema:
    """Get all tags.

    Args:
        session: Database session.

    Returns:
        List of all tags.
    """
    article_repo = ArticleRepository(session)
    tags = await article_repo.get_all_tags()
    return TagsResponseSchema(tags=tags)

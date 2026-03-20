"""FastAPI routes for comments module."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.core.infrastructure.database import get_db_session
from src.modules.articles.infrastructure.repositories import ArticleRepository
from src.modules.auth.infrastructure.repositories import UserRepository
from src.modules.auth.presentation.dependencies import get_current_user, get_optional_user
from src.modules.comments.application.commands.create_comment import CreateComment
from src.modules.comments.application.commands.delete_comment import DeleteComment
from src.modules.comments.application.dtos import (
    CommentDTO,
    CreateCommentRequest,
)
from src.modules.comments.application.queries.list_comments import ListComments
from src.modules.comments.infrastructure.repositories import CommentRepository
from src.modules.comments.presentation.schemas import (
    CommentResponseSchema,
    CommentSchema,
    CreateCommentSchema,
    MultipleCommentsResponseSchema,
    ProfileSchema,
)
from src.modules.profiles.infrastructure.repositories import ProfileRepository

router = APIRouter(prefix="/articles/{slug}/comments", tags=["comments"])


def _comment_dto_to_schema(comment: CommentDTO, following: bool = False) -> CommentSchema:
    """Convert CommentDTO to CommentSchema.

    Args:
        comment: The comment DTO.
        following: Whether the current user is following the author.

    Returns:
        The comment schema.
    """
    return CommentSchema(
        id=comment.id,
        body=comment.body,
        createdAt=comment.created_at,
        updatedAt=comment.updated_at,
        author=ProfileSchema(
            username=comment.author.name,
            bio=comment.author.bio,
            image=comment.author.image,
            following=following,
        ),
    )


@router.post("", response_model=CommentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    slug: str,
    request: CreateCommentSchema,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> CommentResponseSchema:
    """Create a new comment on an article.

    Args:
        slug: The article slug.
        request: The create comment request.
        current_user: The authenticated user.
        session: Database session.

    Returns:
        The created comment.
    """
    comment_repo = CommentRepository(session)
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    # Get article to verify it exists
    article = await article_repo.get_by_slug(slug)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    use_case = CreateComment(comment_repo, user_repo)

    try:
        comment_dto = await use_case.execute(
            CreateCommentRequest(
                body=request.comment.body,
                author_id=current_user["id"],
                article_id=article.id,  # type: ignore
            )
        )

        # Check if following
        following = False
        # Don't check following for own comments

        comment_schema = _comment_dto_to_schema(comment_dto, following)
        return CommentResponseSchema(comment=comment_schema)

    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=MultipleCommentsResponseSchema)
async def list_comments(
    slug: str,
    current_user: dict | None = Depends(get_optional_user),
    session=Depends(get_db_session),
) -> MultipleCommentsResponseSchema:
    """List comments for an article.

    Args:
        slug: The article slug.
        current_user: The authenticated user (optional).
        session: Database session.

    Returns:
        List of comments for the article.
    """
    comment_repo = CommentRepository(session)
    article_repo = ArticleRepository(session)
    user_repo = UserRepository(session)
    profile_repo = ProfileRepository(session)

    # Get article to verify it exists
    article = await article_repo.get_by_slug(slug)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    use_case = ListComments(comment_repo, user_repo)

    try:
        current_user_id = current_user["id"] if current_user else None
        comment_dtos = await use_case.execute(article.id, current_user_id)  # type: ignore

        # Check following status for each comment author
        comment_schemas = []
        for comment_dto in comment_dtos:
            following = False
            if current_user_id and comment_dto.author.name != current_user.get("name"):
                # Get profile to check following status
                author_user = await user_repo.get_by_name(comment_dto.author.name)
                if author_user:
                    following = await profile_repo.is_following(current_user_id, author_user.id)  # type: ignore

            comment_schema = _comment_dto_to_schema(comment_dto, following)
            comment_schemas.append(comment_schema)

        return MultipleCommentsResponseSchema(comments=comment_schemas)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    slug: str,
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    session=Depends(get_db_session),
) -> None:
    """Delete a comment.

    Args:
        slug: The article slug.
        comment_id: The comment ID.
        current_user: The authenticated user.
        session: Database session.
    """
    comment_repo = CommentRepository(session)
    article_repo = ArticleRepository(session)

    # Get article to verify it exists
    article = await article_repo.get_by_slug(slug)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    use_case = DeleteComment(comment_repo)

    try:
        await use_case.execute(comment_id, current_user["id"])
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

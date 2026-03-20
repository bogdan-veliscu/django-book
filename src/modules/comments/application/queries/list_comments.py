"""List comments query."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.comments.application.dtos import CommentAuthorDTO, CommentDTO
from src.modules.comments.domain.repositories import ICommentRepository


class ListComments(IUseCase[tuple[int, int | None], list[CommentDTO]]):
    """Use case for listing comments for an article."""

    def __init__(
        self,
        comment_repository: ICommentRepository,
        user_repository: IUserRepository,
    ) -> None:
        """Initialize use case.

        Args:
            comment_repository: The comment repository.
            user_repository: The user repository.
        """
        self._comment_repository = comment_repository
        self._user_repository = user_repository

    async def execute(
        self, article_id: int, current_user_id: int | None
    ) -> list[CommentDTO]:
        """Execute the list comments use case.

        Args:
            article_id: The article's ID.
            current_user_id: The current user's ID (optional).

        Returns:
            List of comment DTOs.
        """
        # Get comments
        comments = await self._comment_repository.list_by_article(article_id)

        # Convert to DTOs
        comment_dtos = []
        for comment in comments:
            # Get author
            author = await self._user_repository.get(comment.author_id)
            if not author:
                continue  # Skip comments with missing authors

            comment_dto = CommentDTO(
                id=comment.id,  # type: ignore
                body=comment.body,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                author=CommentAuthorDTO(
                    name=author.name,
                    bio=author.bio,
                    image=author.image,
                    following=False,  # Will be populated in route
                ),
            )
            comment_dtos.append(comment_dto)

        return comment_dtos

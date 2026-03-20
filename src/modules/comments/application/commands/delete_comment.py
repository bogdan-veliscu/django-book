"""Delete comment command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.modules.comments.domain.repositories import ICommentRepository


class DeleteComment(IUseCase[tuple[int, int], None]):
    """Use case for deleting a comment."""

    def __init__(self, comment_repository: ICommentRepository) -> None:
        """Initialize use case.

        Args:
            comment_repository: The comment repository.
        """
        self._comment_repository = comment_repository

    async def execute(self, comment_id: int, current_user_id: int) -> None:
        """Execute the delete comment use case.

        Args:
            comment_id: The comment's ID.
            current_user_id: The current user's ID.

        Raises:
            EntityNotFoundException: If comment is not found.
            AuthorizationException: If user is not the author.
        """
        # Get comment
        comment = await self._comment_repository.get(comment_id)
        if not comment:
            raise EntityNotFoundException("Comment", comment_id)

        # Check authorization
        if comment.author_id != current_user_id:
            raise AuthorizationException("Only the author can delete this comment")

        # Delete comment
        await self._comment_repository.delete(comment_id)

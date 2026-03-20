"""Create comment command."""

from src.core.application.use_case import IUseCase
from src.core.domain.exceptions import EntityNotFoundException
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.comments.application.dtos import CommentAuthorDTO, CommentDTO, CreateCommentRequest
from src.modules.comments.domain.entities import Comment
from src.modules.comments.domain.repositories import ICommentRepository


class CreateComment(IUseCase[CreateCommentRequest, CommentDTO]):
    """Use case for creating a comment."""

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

    async def execute(self, request: CreateCommentRequest) -> CommentDTO:
        """Execute the create comment use case.

        Args:
            request: The create comment request.

        Returns:
            The created comment DTO.

        Raises:
            EntityNotFoundException: If author is not found.
        """
        # Create comment
        comment = Comment(
            body=request.body,
            author_id=request.author_id,
            article_id=request.article_id,
        )

        # Save comment
        saved_comment = await self._comment_repository.add(comment)

        # Get author
        author = await self._user_repository.get(saved_comment.author_id)
        if not author:
            raise EntityNotFoundException("User", saved_comment.author_id)

        # Return DTO
        return CommentDTO(
            id=saved_comment.id,  # type: ignore
            body=saved_comment.body,
            created_at=saved_comment.created_at,
            updated_at=saved_comment.updated_at,
            author=CommentAuthorDTO(
                name=author.name,
                bio=author.bio,
                image=author.image,
                following=False,  # Will be populated in route
            ),
        )

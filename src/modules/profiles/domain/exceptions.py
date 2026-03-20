"""Profile domain exceptions."""

from src.core.domain.exceptions import DomainException


class CannotFollowSelfException(DomainException):
    """Raised when a user tries to follow themselves."""

    def __init__(self) -> None:
        """Initialize exception."""
        super().__init__("Cannot follow yourself")

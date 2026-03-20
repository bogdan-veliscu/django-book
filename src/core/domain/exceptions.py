"""Domain exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""

    pass


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""

    def __init__(self, entity_type: str, identifier: str | int) -> None:
        """Initialize exception.

        Args:
            entity_type: The type of entity that was not found.
            identifier: The identifier used to look up the entity.
        """
        super().__init__(f"{entity_type} with identifier '{identifier}' not found")
        self.entity_type = entity_type
        self.identifier = identifier


class EntityAlreadyExistsException(DomainException):
    """Raised when trying to create an entity that already exists."""

    def __init__(self, entity_type: str, identifier: str | int) -> None:
        """Initialize exception.

        Args:
            entity_type: The type of entity that already exists.
            identifier: The identifier of the existing entity.
        """
        super().__init__(f"{entity_type} with identifier '{identifier}' already exists")
        self.entity_type = entity_type
        self.identifier = identifier


class ValidationException(DomainException):
    """Raised when domain validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize exception.

        Args:
            message: The validation error message.
            field: The field that failed validation (optional).
        """
        super().__init__(message)
        self.field = field


class AuthorizationException(DomainException):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, message: str = "Not authorized to perform this action") -> None:
        """Initialize exception.

        Args:
            message: The authorization error message.
        """
        super().__init__(message)

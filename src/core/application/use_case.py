"""Base use case interfaces."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class IUseCase(ABC, Generic[TRequest, TResponse]):
    """Base interface for use cases.

    Use cases represent application-specific business logic and orchestrate
    the flow of data to and from entities and repositories. They are the entry
    points to the application layer.
    """

    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse:
        """Execute the use case.

        Args:
            request: The input data for the use case.

        Returns:
            The result of executing the use case.
        """
        pass

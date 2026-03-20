"""Data Transfer Objects (DTOs)."""

from pydantic import BaseModel, ConfigDict


class DTO(BaseModel):
    """Base class for Data Transfer Objects.

    DTOs are used to transfer data between layers. They are immutable and
    validated using Pydantic.
    """

    model_config = ConfigDict(
        frozen=True,
        from_attributes=True,
    )

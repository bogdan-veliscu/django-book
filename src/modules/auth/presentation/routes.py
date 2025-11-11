"""Auth API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core.presentation.dependencies import (
    get_current_user_id,
    get_jwt_service,
    get_user_repository,
)
from src.modules.auth.application.commands.login_user import LoginUser
from src.modules.auth.application.commands.register_user import RegisterUser
from src.modules.auth.application.dtos import LoginUserRequest, RegisterUserRequest
from src.modules.auth.domain.repositories import IUserRepository
from src.modules.auth.infrastructure.jwt import JWTService
from src.modules.auth.presentation.schemas import (
    AuthResponse,
    AuthResponseWrapper,
    LoginRequestWrapper,
    RegisterRequestWrapper,
    UserResponse,
    UserResponseWrapper,
)

router = APIRouter()


@router.post(
    "/users",
    response_model=AuthResponseWrapper,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: RegisterRequestWrapper,
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> AuthResponseWrapper:
    """Register a new user.

    Args:
        request: The registration request.
        user_repository: The user repository.
        jwt_service: The JWT service.

    Returns:
        The registered user with authentication token.
    """
    use_case = RegisterUser(user_repository, jwt_service)

    # Convert Pydantic model to DTO
    dto_request = RegisterUserRequest(
        email=request.user.email,
        name=request.user.name,
        password=request.user.password,
    )

    result = await use_case.execute(dto_request)

    return AuthResponseWrapper(
        user=AuthResponse(
            email=result.user.email,
            token=result.token,
            name=result.user.name,
            bio=result.user.bio,
            image=result.user.image,
        )
    )


@router.post(
    "/users/login",
    response_model=AuthResponseWrapper,
    summary="Login existing user",
)
async def login(
    request: LoginRequestWrapper,
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
) -> AuthResponseWrapper:
    """Login an existing user.

    Args:
        request: The login request.
        user_repository: The user repository.
        jwt_service: The JWT service.

    Returns:
        The authenticated user with token.
    """
    use_case = LoginUser(user_repository, jwt_service)

    # Convert Pydantic model to DTO
    dto_request = LoginUserRequest(
        email=request.user.email,
        password=request.user.password,
    )

    result = await use_case.execute(dto_request)

    return AuthResponseWrapper(
        user=AuthResponse(
            email=result.user.email,
            token=result.token,
            name=result.user.name,
            bio=result.user.bio,
            image=result.user.image,
        )
    )


@router.get(
    "/user",
    response_model=UserResponseWrapper,
    summary="Get current user",
)
async def get_current_user(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
) -> UserResponseWrapper:
    """Get current authenticated user.

    Args:
        current_user_id: The current user's ID.
        user_repository: The user repository.

    Returns:
        The current user's information.
    """
    user = await user_repository.get(current_user_id)

    if not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="User not found")

    return UserResponseWrapper(
        user=UserResponse(
            id=user.id,  # type: ignore
            email=user.email.value,
            name=user.name,
            bio=user.bio,
            image=user.image,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    )

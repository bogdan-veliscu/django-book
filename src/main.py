"""Main FastAPI application."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from src.config import Settings, get_settings
from src.core.domain.exceptions import (
    AuthorizationException,
    DomainException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
    ValidationException,
)
from src.core.infrastructure import cache, database


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    settings = get_settings()

    # Initialize database
    database.db_manager = database.DatabaseManager(
        database_url=str(settings.database_url),
        echo=settings.database_echo,
    )

    # Create tables (in production, use Alembic migrations)
    if settings.environment == "development":
        await database.db_manager.create_all()

    # Initialize cache
    cache.cache_manager = cache.CacheManager(redis_url=str(settings.redis_url))

    yield

    # Cleanup
    await database.db_manager.close()
    await cache.cache_manager.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Register exception handlers
    register_exception_handlers(app)

    # Register routers
    from src.modules.auth.presentation.routes import router as auth_router
    from src.modules.profiles.presentation.routes import router as profiles_router
    from src.modules.articles.presentation.routes import (
        router as articles_router,
        tags_router,
    )

    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(profiles_router, prefix="/api", tags=["profiles"])
    app.include_router(articles_router, prefix="/api", tags=["articles"])
    app.include_router(tags_router, prefix="/api", tags=["tags"])
    # from src.modules.comments.presentation.routes import router as comments_router
    # app.include_router(comments_router, prefix="/api", tags=["comments"])

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers.

    Args:
        app: The FastAPI application.
    """

    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(
        request: Any,
        exc: EntityNotFoundException,
    ) -> JSONResponse:
        """Handle entity not found exceptions."""
        return JSONResponse(
            status_code=404,
            content={"errors": {"body": [str(exc)]}},
        )

    @app.exception_handler(EntityAlreadyExistsException)
    async def entity_already_exists_handler(
        request: Any,
        exc: EntityAlreadyExistsException,
    ) -> JSONResponse:
        """Handle entity already exists exceptions."""
        return JSONResponse(
            status_code=422,
            content={"errors": {"body": [str(exc)]}},
        )

    @app.exception_handler(ValidationException)
    async def validation_exception_handler(
        request: Any,
        exc: ValidationException,
    ) -> JSONResponse:
        """Handle validation exceptions."""
        field = exc.field or "body"
        return JSONResponse(
            status_code=422,
            content={"errors": {field: [str(exc)]}},
        )

    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(
        request: Any,
        exc: AuthorizationException,
    ) -> JSONResponse:
        """Handle authorization exceptions."""
        return JSONResponse(
            status_code=403,
            content={"errors": {"body": [str(exc)]}},
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(
        request: Any,
        exc: DomainException,
    ) -> JSONResponse:
        """Handle generic domain exceptions."""
        return JSONResponse(
            status_code=400,
            content={"errors": {"body": [str(exc)]}},
        )


# Create the app instance
app = create_app()

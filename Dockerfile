# Build stage for dependencies
FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv
# Set up working directory
WORKDIR /code

# Place executables in the environment at the front of the path
ENV PATH="/code/.venv/bin:$PATH"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies without project code for caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy application code
COPY ./pyproject.toml ./uv.lock ./README.md /code/

# Finalize dependency installation in non-editable mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Add entrypoint script and set permissions in the builder stage
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

FROM python:3.12-slim-bookworm AS app

# Ensure UV is available
COPY --from=builder /bin/uv /bin/uv
COPY --from=builder /code/.venv /code/.venv
COPY --from=builder /code /code
COPY . /code/

# Configure environment variables for the virtual environment
ENV VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH" \
    PYTHONPATH=/code:$PYTHONPATH

# Expose application port
EXPOSE 8000

# Default environment variables
ENV HOST=0.0.0.0 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE="config.settings.production"

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

WORKDIR /code

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

# Metadata
LABEL maintainer="Bogdan Veliscu" \
    version="1.0" \
    description="Production-ready Django application with uv and optimized Docker image"
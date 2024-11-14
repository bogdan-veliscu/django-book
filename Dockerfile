# Build stage for dependencies
FROM python:3.12-slim-bookworm as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set up working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency management files
COPY pyproject.toml uv.lock ./

# Install dependencies without project code for caching
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable

# Copy application code
COPY . .

# Finalize dependency installation in non-editable mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable

# Add entrypoint script and set permissions in the builder stage
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Final stage
FROM python:3.12-slim-bookworm AS app

# Set up a non-root user for security
RUN useradd -ms /bin/bash appuser

# Set up working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Configure environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy application source files only
COPY --from=builder /app /app

# Copy the entrypoint script with permissions already set
COPY --from=builder /entrypoint.sh /entrypoint.sh

# Set permissions for the application directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Default environment variables
ENV HOST=0.0.0.0 \
    PORT=8000

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use environment variables for CMD
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "config.asgi:application", "--host", "${HOST}", "--port", "${PORT}"]

# Metadata
LABEL maintainer="Bogdan Veliscu" \
    version="1.0" \
    description="Production-ready Django application with uv and optimized Docker image"
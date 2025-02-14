# Build stage for dependencies
FROM python:3.12-slim-bookworm AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set up working directory
WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create and activate virtual environment
RUN uv venv /code/.venv
ENV PATH="/code/.venv/bin:$PATH" \
    VIRTUAL_ENV="/code/.venv"

# Copy dependency files and README
COPY pyproject.toml README.md ./

# Install dependencies in development mode
RUN uv pip install -e .

# Copy application code
COPY . .

# Add entrypoint script
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh

FROM python:3.12-slim-bookworm AS app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder stage
COPY --from=builder /code/.venv /code/.venv
COPY --from=builder /code /code
COPY --from=builder /code/entrypoint.sh /entrypoint.sh

WORKDIR /code

# Set environment variables
ENV PATH="/code/.venv/bin:$PATH" \
    VIRTUAL_ENV="/code/.venv" \
    PYTHONPATH=/code/conduit \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE="config.settings.production"

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Set entrypoint and command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "conduit.config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

# Metadata
LABEL maintainer="Bogdan Veliscu" \
    version="1.0" \
    description="Production-ready Django application with uv and optimized Docker image"
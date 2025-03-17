# Build stage for dependencies
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /code

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_SECRET_KEY=dummy \
    PYTHONPATH=/code \
    PIP_INDEX_URL=https://pypi.org/simple/ \
    PIP_RETRIES=10 \
    PIP_TIMEOUT=100

# Create virtual environment
RUN python -m venv /code/.venv
ENV PATH="/code/.venv/bin:$PATH" \
    VIRTUAL_ENV="/code/.venv"

# Copy dependency files
COPY pyproject.toml README.md ./

# Generate locked requirements
RUN uv pip compile pyproject.toml -o requirements.txt

# Install dependencies using uv with retries
RUN --mount=type=cache,target=/root/.cache/uv \
    for i in $(seq 1 3); do \
    uv pip install --no-cache-dir -r requirements.txt && break || sleep 5; \
    done

# Copy application code
COPY ./conduit ./conduit/
COPY config ./config/
COPY locustfile.py ./
COPY entrypoint.sh ./

# Install the package in development mode with retries
RUN for i in $(seq 1 3); do \
    pip install -e . && break || sleep 5; \
    done

# Prepare static files and verify Django setup
WORKDIR /code/conduit
RUN mkdir -p staticfiles media logs && \
    DJANGO_SETTINGS_MODULE=config.settings.base \
    python manage.py collectstatic --noinput --clear

# Production stage
FROM python:3.12-slim-bookworm as app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    PATH="/code/.venv/bin:$PATH" \
    VIRTUAL_ENV="/code/.venv"

# Copy virtual environment and code from builder
COPY --from=builder /code /code

WORKDIR /code/conduit

# Make entrypoint executable
RUN chmod +x /code/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["uvicorn"]

# Metadata
LABEL maintainer="Bogdan Veliscu" \
    version="1.0" \
    description="Production-ready Django application with uv and optimized Docker image"
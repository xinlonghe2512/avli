# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# Set working directory
WORKDIR /src

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libc-dev \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set .venv in PATH for all commands
ENV PATH="/src/.venv/bin:$PATH"

# Compile bytecode & force copy mode (for mounted volumes)
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies using BuildKit mounts (efficient caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=services/asset-intel-service/pyproject.toml,target=services/asset-intel-service/pyproject.toml \
    uv sync --locked --no-install-project --no-dev --package avli-asset-intel-service

# Copy the rest of the application
COPY . /src

# Sync again after copying the project files
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --package avli-asset-intel-service

# Run Celery worker
CMD ["uv", "run", "--no-sync", "celery", "-A", "app.worker", "worker", "--loglevel=info"]

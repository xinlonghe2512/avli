# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

# Set working directory
WORKDIR /src

# Install system dependencies and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libc-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set .venv in PATH for all commands.
ENV PATH="/src/.venv/bin:$PATH"

# Compile bytecode & force copy mode (for mounted volumes)
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy only the files required to resolve the workspace.
COPY pyproject.toml uv.lock ./

COPY services/asset-intel-service/pyproject.toml \
    services/asset-intel-service/README.md \
    services/asset-intel-service/

# Install dependencies first for better layer caching.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
    --locked \
    --no-install-project \
    --no-dev \
    --package avli-asset-intel-service

# Now copy the actual application source.
COPY services/asset-intel-service/src ./src

# Install the application itself.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
    --locked \
    --no-dev \
    --package avli-asset-intel-service


FROM docker.io/python:3.13-slim-trixie AS runtime

WORKDIR /src

# Runtime environment.
ENV PATH="/src/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the already-built virtual environment.
COPY --from=builder /src/.venv /src/.venv

# Copy application source.
COPY --from=builder /src/src /src/src

# Expose app port
EXPOSE 8000

CMD ["uvicorn", "src.main:service", "--host", "0.0.0.0", "--port", "8000"]

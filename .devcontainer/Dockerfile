FROM mcr.microsoft.com/devcontainers/python:3.13-trixie

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  bash \
  build-essential \
  ca-certificates \
  curl \
  gh \
  jq \
  ripgrep \
  fd-find \
  fzf \
  bat \
  make \
  shellcheck \
  tar \
  unzip \
  wget \
  zip \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never

WORKDIR /workspace/avli

# Copy only dependency metadata for Docker layer caching.
COPY --chown=vscode:vscode \
  pyproject.toml \
  uv.lock \
  ./

COPY --chown=vscode:vscode \
  apps/asset-intel-service/pyproject.toml \
  apps/asset-intel-service/pyproject.toml

USER vscode

RUN uv sync --frozen

ENV PATH="/workspace/avli/.venv/bin:$PATH"

CMD ["sleep", "infinity"]

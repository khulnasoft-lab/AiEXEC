# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit


################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################

# 1. use python:3.12.3-slim as the base image until https://github.com/pydantic/pydantic-core/issues/1292 gets resolved
# 2. do not add --platform=$BUILDPLATFORM because the pydantic binaries must be resolved for the final architecture
# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    # deps for building python deps
    build-essential \
    git \
    # npm
    npm \
    # gcc
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install the project's dependencies using the lockfile and settings
# We need to mount the root uv.lock and pyproject.toml to build the base with uv because we're still using uv workspaces
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=api/base/README.md,target=api/base/README.md \
    --mount=type=bind,source=api/base/uv.lock,target=api/base/uv.lock \
    --mount=type=bind,source=api/base/pyproject.toml,target=api/base/pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    cd api/base && uv sync --frozen --no-install-project --no-dev --no-editable --extra postgresql

COPY ./api /app/src

COPY web /tmp/web
WORKDIR /tmp/web
RUN npm install \
    && npm run build \
    && cp -r build /app/api/base/aiexec/frontend \
    && rm -rf /tmp/web

COPY ./api/base /app/api/base
WORKDIR /app/api/base
# again we need these because of workspaces
COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock
COPY ./api/base/pyproject.toml /app/api/base/pyproject.toml
COPY ./api/base/uv.lock /app/api/base/uv.lock
COPY ./api/base/README.md /app/api/base/README.md
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --extra postgresql

################################
# RUNTIME
# Setup user, utilities and copy the virtual environment only
################################
FROM python:3.12.3-slim AS runtime

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y git libpq5 curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd user -u 1000 -g 0 --no-create-home --home-dir /app/data
# and we use the venv at the root because workspaces
COPY --from=builder --chown=1000 /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

LABEL org.opencontainers.image.title=aiexec
LABEL org.opencontainers.image.authors=['Aiexec']
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.url=https://github.com/khulnasoft-lab/aiexec
LABEL org.opencontainers.image.source=https://github.com/khulnasoft-lab/aiexec

USER user
WORKDIR /app

ENV AIEXEC_HOST=0.0.0.0
ENV AIEXEC_PORT=7860

CMD ["aiexec-base", "run"]

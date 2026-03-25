# Stage 1: Build with uv
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Copy project files for dependency resolution
COPY pyproject.toml uv.lock /app/
COPY bot/pyproject.toml /app/bot/pyproject.toml

# Sync dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy bot source code
COPY bot /app/bot

# Install the bot project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Stage 2: Runtime image
FROM python:3.14-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy bot source code
COPY --from=builder /app/bot /app/bot
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/uv.lock /app/uv.lock

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Set working directory for bot
WORKDIR /app/bot

# Run the bot directly using Python from venv
CMD ["python", "bot.py"]

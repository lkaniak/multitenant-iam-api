FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
COPY packages/notification-service packages/notification-service
RUN uv sync --frozen --no-dev --no-install-project

COPY src src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8150

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8150", "--app-dir", "/app/src"]

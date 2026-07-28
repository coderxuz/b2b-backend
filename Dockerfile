FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container
WORKDIR /app
COPY . /app

# Install the application dependencies
RUN uv sync --frozen --no-cache

# Default command
CMD ["/app/.venv/bin/uvicorn", "main:app", "--port", "8001", "--host", "0.0.0.0"]

FROM python:3.11-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY .python-version .

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY *.py .
COPY config/ config/
COPY data/ data/

# Expose port
EXPOSE 8050

# Run dashboard
CMD ["uv", "run", "python", "dashboard.py"]

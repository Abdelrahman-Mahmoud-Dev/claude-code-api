FROM python:3.12-slim

# Install system deps (curl for Poetry installer)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry globally
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Note: Claude Code CLI is bundled with claude-agent-sdk >= 0.1.8
# No separate Node.js/npm installation required

# Set default port (override via -e PORT=9514)
ENV PORT=8000

# Copy the app code
COPY . /app

# Set working directory
WORKDIR /app

# Install Python dependencies with Poetry (no dev dependencies for production)
RUN poetry install --no-root --without dev

# Expose the port
EXPOSE ${PORT}

# Run the app with Uvicorn in production mode
CMD poetry run uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 2 --access-log
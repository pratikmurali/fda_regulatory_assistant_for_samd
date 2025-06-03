FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock .

# Install uv package manager
RUN pip install --no-cache-dir uv

# Install Python dependencies using uv
RUN uv pip install --system --no-cache -r pyproject.toml

# Ensure we have the latest versions of critical packages
RUN uv pip install --system --no-cache --upgrade \
    langsmith \
    chainlit \
    langgraph \
    langchain \
    langchain-openai

# Copy application files
COPY main.py .
COPY chainlit.md .
COPY chainlit.yaml .
COPY README.md .

# Copy source code directories
COPY agents/ ./agents/
COPY evals/ ./evals/
COPY examples/ ./examples/
COPY graph/ ./graph/
COPY loaders/ ./loaders/
COPY prompts/ ./prompts/
COPY ragchains/ ./ragchains/
COPY tests/ ./tests/
COPY tools/ ./tools/
COPY utils/ ./utils/

# Copy public assets
COPY public/ ./public/

# Create necessary directories and set permissions
RUN mkdir -p cache && \
    mkdir -p cybersecurity-cache && \
    mkdir -p /app/.files && \
    mkdir -p /tmp && \
    chmod -R 777 /app/cache && \
    chmod -R 777 /app/cybersecurity-cache && \
    chmod -R 777 /app/.files && \
    chmod -R 777 /tmp

# Create a non-root user
RUN useradd -m -u 1000 user

# Change ownership of the app directory to the non-root user
RUN chown -R user:user /app

# Switch to the non-root user
USER user

# Set environment variables for Hugging Face Spaces
ENV HOME=/app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# AWS configuration for anonymous access to public S3 buckets
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_REGION="us-east-1"

# Environment variables that will be overridden by Hugging Face Spaces secrets
ENV OPENAI_API_KEY=""
ENV LANGCHAIN_API_KEY=""
ENV LANGCHAIN_TRACING_V2="false"
ENV LANGCHAIN_PROJECT="fda-regulatory-assistant"

# Redis configuration (will use in-memory cache if Redis not available)
ENV REDIS_URL="redis://127.0.0.1:6379"

# Chainlit configuration
ENV CHAINLIT_HOST="0.0.0.0"
ENV CHAINLIT_PORT="7860"

# Expose port required by Hugging Face Spaces
EXPOSE 7860

# Command to run the application
CMD ["chainlit", "run", "main.py", "--host", "0.0.0.0", "--port", "7860"]

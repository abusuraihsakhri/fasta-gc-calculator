FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only what's needed first for better layer caching
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install core dependencies (stdlib is sufficient, but pydantic is used by agents/)
RUN pip install --no-cache-dir pydantic pytest

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command runs in interactive CLI mode
# For FastAPI server, use: docker run ... python -m agents.api
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]

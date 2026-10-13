FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# The calculator itself uses only the Python standard library.
# FastAPI and Pydantic are retained for the optional agent/API components.
RUN pip install --no-cache-dir "pydantic>=2,<3" "fastapi>=0.110,<1" "uvicorn>=0.30,<1"

COPY . .

# Default container use: docker run ... gc --sequence ATCG
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]

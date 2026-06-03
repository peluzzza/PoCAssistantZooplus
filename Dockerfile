# zooplus Assistant PoC — production profile (v2.0)
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ZOOPLUS_RETRIEVAL_MODE=hybrid \
    ZOOPLUS_VECTOR_BACKEND=chroma_local

WORKDIR /app

COPY pyproject.toml README.md ./
COPY cli ./cli
COPY src ./src
COPY data ./data
COPY scripts ./scripts

RUN pip install --no-cache-dir -e ".[rag]" \
    && python -m cli ingest

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8080"]

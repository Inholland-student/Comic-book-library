FROM python:3.11-slim

# OCI Image Metadata (helps with SBOM generation and artifact tracking)
LABEL org.opencontainers.image.title="Comic Book Library Backend"
LABEL org.opencontainers.image.description="Flask REST API backend for Comic Book Library"
LABEL org.opencontainers.image.authors="Comic Book Library Team"
LABEL org.opencontainers.image.url="https://github.com/meryamdouiri/Comic-book-library"
LABEL org.opencontainers.image.source="https://github.com/meryamdouiri/Comic-book-library"
LABEL org.opencontainers.image.documentation="https://github.com/meryamdouiri/Comic-book-library/blob/main/README.md"
LABEL org.opencontainers.image.vendor="Comic Book Library"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY data ./data

RUN chmod +x entrypoint.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()"

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "run.py"]
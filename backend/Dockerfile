FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/python3.11/site-packages

COPY --from=builder /root/.local /home/app/.local

RUN useradd -m -u 1001 -s /bin/sh app && chown -R app:app /app /home/app

USER app

ENV PATH=/home/app/.local/bin:$PATH

COPY --chown=app:app . .

RUN chmod +x entrypoint.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()"

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "run.py"]

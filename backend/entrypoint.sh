#!/bin/bash
set -eu

export PYTHONPATH="/app${PYTHONPATH:+:$PYTHONPATH}"

wait_for_db() {
    echo "[entrypoint] Waiting for database to accept connections..."
    retries=30
    until [ $retries -le 0 ]; do
        if python - <<'PY' 1>/dev/null 2>&1
import os
import mysql.connector
from mysql.connector import Error

try:
    mysql.connector.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ.get('DB_PORT', '3306')),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        connect_timeout=5,
    ).close()
except Error:
    raise SystemExit(1)
PY
        then
            echo "[entrypoint] Database is ready."
            return
        fi
        retries=$((retries - 1))
        echo "[entrypoint] Database not ready yet, retrying... ($retries attempts left)"
        sleep 2
    done

    echo "[entrypoint] Unable to connect to database after multiple retries." >&2
    exit 1
}

run_import() {
    cmd=(python scripts/load_comics_from_csv.py)
    if [ -n "${IMPORT_CREATED_BY:-}" ]; then
        cmd+=(--created-by "${IMPORT_CREATED_BY}")
    fi
    echo "[entrypoint] Running: ${cmd[*]}"
    "${cmd[@]}"
}

wait_for_db
run_import

exec "$@"

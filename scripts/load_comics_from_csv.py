"""Utility to refresh the `comics` table from `data/comic_digital.csv`."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import mysql.connector
from mysql.connector import Error

from app.config import Config


DEFAULT_CSV = Path(__file__).resolve().parents[1] / "data" / "comic_digital.csv"
CSV_FIELDNAMES = ("id", "serie", "number", "title")


def get_connection() -> mysql.connector.connection_cext.CMySQLConnection:
    """Return a MySQL connection using the Flask app config."""

    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=False,
        )
    except Error as error:
        print(f"[ERROR] Unable to connect to database: {error}")
        raise


def find_default_creator(cursor) -> int:
    """Pick an existing super_admin or admin to attribute the imported comics to."""

    for role in ("super_admin", "admin"):
        cursor.execute("SELECT id FROM users WHERE role = %s ORDER BY id LIMIT 1", (role,))
        row = cursor.fetchone()
        if row:
            return row[0]

    raise RuntimeError(
        "No super_admin or admin user exists in the database; create one before importing comics."
    )


def truncate_comics_table(cursor) -> None:
    """Empty the comics table (and reset the auto increment)."""

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("TRUNCATE TABLE comics")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def import_csv(cursor, csv_path: Path, created_by: int, batch_size: int = 1000) -> int:
    """Insert rows from the CSV, returning how many comics were imported."""

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, fieldnames=CSV_FIELDNAMES)
        next(reader, None)  # skip header

        batch = []
        inserted = 0

        for row in reader:
            serie = row.get("serie", "").strip()
            number = row.get("number", "").strip()
            title = row.get("title", "").strip()

            if not serie or not number or not title:
                continue

            batch.append((serie, number, title, created_by))

            if len(batch) >= batch_size:
                cursor.executemany(
                    "INSERT INTO comics (serie, number, title, created_by) VALUES (%s, %s, %s, %s)",
                    batch,
                )
                inserted += len(batch)
                batch.clear()

        if batch:
            cursor.executemany(
                "INSERT INTO comics (serie, number, title, created_by) VALUES (%s, %s, %s, %s)",
                batch,
            )
            inserted += len(batch)

    return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Truncate the comics table and populate it from data/comic_digital.csv"
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Path to the CSV file to load",
    )
    parser.add_argument(
        "--created-by",
        type=int,
        help="User ID used for the created_by foreign key; falls back to the first admin",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="How many rows to insert per batch (defaults to 1000)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            print("[INFO] Truncating comics table...")
            truncate_comics_table(cursor)

            created_by = args.created_by
            if created_by is None:
                created_by = find_default_creator(cursor)
                print(f"[INFO] No --created-by passed; using user id={created_by}.")

            print(f"[INFO] Importing comics from {args.csv} (created_by={created_by})")
            inserted = import_csv(cursor, args.csv, created_by, batch_size=args.batch_size)

            connection.commit()
            print(f"[INFO] Imported {inserted} comics.")
    except (Error, FileNotFoundError, RuntimeError) as err:
        print(f"[ERROR] {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()

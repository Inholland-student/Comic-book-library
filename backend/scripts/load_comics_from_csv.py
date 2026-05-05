"""Utility to refresh the `comics` table from `data/comic_digital.csv`."""

from __future__ import annotations

import argparse
import csv
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.features.common.persistence.db import db
from app.features.comics.comic import Comic
from app.features.auth.user import User, UserRole

DEFAULT_CSV = Path(__file__).resolve().parents[1] / "data" / "comic_digital.csv"
CSV_FIELDNAMES = ("id", "serie", "number", "title")


def find_default_creator() -> int:
    """Pick an existing super_admin or admin to attribute the imported comics to."""
    for role in (UserRole.super_admin, UserRole.admin):
        user = db.session.query(User).filter_by(role=role).order_by(User.id).first()
        if user:
            return user.id

    raise RuntimeError(
        "No super_admin or admin user exists in the database; create one before importing comics."
    )


def truncate_comics_table() -> None:
    """Empty the comics table and reset auto increment."""
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
    db.session.execute(db.text("TRUNCATE TABLE comics"))
    db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
    db.session.commit()


def import_csv(csv_path: Path, created_by: int, batch_size: int = 1000) -> int:
    """Insert rows from the CSV, returning how many comics were imported."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    inserted = 0
    batch = []

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, fieldnames=CSV_FIELDNAMES)
        next(reader, None)  # skip header

        for row in reader:
            serie = row.get("serie", "").strip()
            number = row.get("number", "").strip()
            title = row.get("title", "").strip()

            if not serie or not number or not title:
                continue

            batch.append(
                Comic(serie=serie, number=number, title=title, created_by=created_by)
            )

            if len(batch) >= batch_size:
                db.session.bulk_save_objects(batch)
                db.session.commit()
                inserted += len(batch)
                batch.clear()

        if batch:
            db.session.bulk_save_objects(batch)
            db.session.commit()
            inserted += len(batch)

    return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Truncate the comics table and populate it from data/comic_digital.csv"
    )
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--created-by", type=int)
    parser.add_argument("--batch-size", type=int, default=1000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = create_app()

    with app.app_context():
        try:
            print("[INFO] Truncating comics table...")
            truncate_comics_table()

            created_by = args.created_by
            if created_by is None:
                created_by = find_default_creator()
                print(f"[INFO] No --created-by passed; using user id={created_by}.")

            print(f"[INFO] Importing comics from {args.csv} (created_by={created_by})")
            inserted = import_csv(args.csv, created_by, batch_size=args.batch_size)
            print(f"[INFO] Imported {inserted} comics.")

        except (FileNotFoundError, RuntimeError) as err:
            print(f"[ERROR] {err}")
            sys.exit(1)


if __name__ == "__main__":
    main()

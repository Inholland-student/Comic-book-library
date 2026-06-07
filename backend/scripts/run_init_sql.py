"""Seed script — creates admin and super_admin users if they don't exist."""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from app.features.common.persistence.db import db

SEED_USERS = [
    {
        "username": "admin",
        "email": "admin@mail.com",
        "password": "changeme",
        "role": "admin",
    },
    {
        "username": "super_admin",
        "email": "super_admin@mail.com",
        "password": "changeme",
        "role": "super_admin",
    },
]


def seed_users() -> None:
    from app.features.auth.user import User, UserRole
    from app.features.auth.password_service import hash_password

    role_map = {"admin": UserRole.admin, "super_admin": UserRole.super_admin}

    for data in SEED_USERS:
        exists = db.session.query(User).filter_by(username=data["username"]).first()
        if exists:
            print(f"[INFO] User '{data['username']}' already exists, skipping.")
            continue

        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role=role_map[data["role"]],
        )
        db.session.add(user)
        print(f"[INFO] Created user '{data['username']}' with role '{data['role']}'.")

    db.session.commit()


def main() -> None:
    app = create_app()
    with app.app_context():
        seed_users()


if __name__ == "__main__":
    main()

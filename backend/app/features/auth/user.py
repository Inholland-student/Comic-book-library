import enum
from datetime import datetime
from app.features.common.persistence.db import db


class UserRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    friend = "friend"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(
        db.CHAR(36), nullable=False, unique=True, server_default=db.text("(uuid())")
    )
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.friend)
    created_at = db.Column(
        db.TIMESTAMP, nullable=True, server_default=db.text("CURRENT_TIMESTAMP")
    )
    updated_at = db.Column(
        db.TIMESTAMP,
        nullable=True,
        server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    comics = db.relationship("Comic", back_populates="creator", cascade="all, delete")

    def __repr__(self):
        return f"<User {self.id} - {self.username}>"

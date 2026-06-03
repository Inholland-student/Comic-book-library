from datetime import datetime
from app.features.common.persistence.db import db


class Comic(db.Model):
    __tablename__ = "comics"

    __table_args__ = (
        db.Index("idx_serie", "serie"),
        db.Index("idx_created_by", "created_by"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serie = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    created_by = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(
        db.TIMESTAMP, nullable=True, server_default=db.text("CURRENT_TIMESTAMP")
    )
    updated_at = db.Column(
        db.TIMESTAMP,
        nullable=True,
        server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    creator = db.relationship("User", back_populates="comics")

    def __repr__(self):
        return f"<Comic {self.id} - {self.title}>"

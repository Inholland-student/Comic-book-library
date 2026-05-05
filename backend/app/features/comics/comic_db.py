from app.features.common.persistence.db import db
from .comic import Comic  # SQLAlchemy model


def get_all_comics() -> list[Comic]:
    """Retrieve all comics from database, ordered by created_at DESC."""
    return db.session.query(Comic).order_by(Comic.created_at.desc()).all()


def count_comics() -> int:
    """Return total number of comics."""
    return db.session.query(Comic).count()


def get_comics_page(limit: int, offset: int) -> list[Comic]:
    """Retrieve a paginated slice of comics."""
    return (
        db.session.query(Comic)
        .order_by(Comic.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_comic_by_id(comic_id: int) -> Comic | None:
    """Retrieve comic by ID. Returns Comic or None if not found."""
    return db.session.get(Comic, comic_id)


def create_comic(serie: str, number: str, title: str, created_by: int) -> Comic:
    """
    Create a new comic.

    Args:
        serie: Comic series name
        number: Issue number
        title: Comic title
        created_by: User ID of creator (FK to users.id)

    Returns:
        Newly created Comic object

    Raises:
        SQLAlchemyError: If DB error (e.g., invalid created_by FK)
    """
    comic = Comic(serie=serie, number=number, title=title, created_by=created_by)

    db.session.add(comic)
    db.session.commit()
    db.session.refresh(comic)

    return comic


def update_comic(comic_id: int, serie: str, number: str, title: str) -> Comic | None:
    """
    Update an existing comic.

    Args:
        comic_id: ID of comic to update
        serie: New series name
        number: New issue number
        title: New title

    Returns:
        Updated Comic object, or None if not found
    """
    comic = db.session.get(Comic, comic_id)

    if not comic:
        return None

    comic.serie = serie
    comic.number = number
    comic.title = title

    db.session.commit()
    db.session.refresh(comic)

    return comic


def delete_comic(comic_id: int) -> bool:
    """
    Delete a comic by ID.

    Args:
        comic_id: ID of comic to delete

    Returns:
        True if deleted, False if not found

    Raises:
        SQLAlchemyError: If DB error
    """
    comic = db.session.get(Comic, comic_id)

    if not comic:
        return False

    db.session.delete(comic)
    db.session.commit()

    return True

from app.features.common.persistence.db import db
from .user import User, UserRole
from .password_service import hash_password


def get_user_by_username(username: str) -> User | None:
    """Retrieve user by username. Returns User or None if not found."""
    return db.session.query(User).filter_by(username=username).first()


def get_user_by_uuid(user_uuid: str) -> User | None:
    """Retrieve user by UUID. Returns User or None if not found."""
    return db.session.query(User).filter_by(uuid=user_uuid).first()


def get_user_by_email(email: str) -> User | None:
    """Retrieve user by email. Returns User or None if not found."""
    return db.session.query(User).filter_by(email=email).first()


def get_user_id_by_uuid(user_uuid: str) -> int | None:
    """Gets internal user ID by UUID."""
    user = db.session.query(User.id).filter_by(uuid=user_uuid).first()
    return user.id if user else None


def create_user(username: str, email: str, password_plaintext: str, role: str) -> User:
    """
    Create a new user with bcrypt-hashed password.

    Args:
        username: Unique username
        email: Unique email
        password_plaintext: Plaintext password (will be hashed)
        role: One of 'super_admin', 'admin', 'friend'

    Returns:
        Newly created User object

    Raises:
        ValueError: If role is invalid
        SQLAlchemyError: If DB error (e.g., duplicate username/email)
    """
    # Validate role before DB operation
    try:
        user_role = UserRole(role)
    except ValueError:
        valid = [r.value for r in UserRole]
        raise ValueError(f"Invalid role '{role}'. Must be one of: {valid}")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password_plaintext),
        role=user_role,
    )

    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)

    return user

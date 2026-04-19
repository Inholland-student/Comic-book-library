from app.features.common.persistence.db import get_connection
from .user import User, VALID_ROLES
from .password_service import hash_password
from mysql.connector import Error

def get_user_by_username(username: str):
    """
    Retrieve user by username
    Returns User object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query prevents SQL injection
        query = "SELECT id, uuid, username, email, password_hash, role, created_at, updated_at FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row[0],
                uuid=row[1], 
                username=row[2],
                email=row[3],
                password_hash=row[4],
                role=row[5],
                created_at=row[6],
                updated_at=row[7]
            )
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_by_uuid(user_uuid: str):
    """
    Retrieve user by ID
    Returns User object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query
        query = "SELECT id, uuid, username, email, password_hash, role, created_at, updated_at FROM users WHERE uuid = %s"
        cursor.execute(query, (user_uuid,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row[0],
                uuid=row[1],
                username=row[2],
                email=row[3],
                password_hash=row[4],
                role=row[5],
                created_at=row[6],
                updated_at=row[7]
            )
        return None
    finally:
        cursor.close()
        conn.close()


def create_user(username: str, email: str, password_plaintext: str, role: str):
    """
    Create a new user with bcrypt-hashed password
    
    Args:
        username: Unique username
        email: Unique email
        password_plaintext: Plaintext password (will be hashed)
        role: One of 'super_admin', 'admin', 'friend'
    
    Returns:
        User object if created successfully
    
    Raises:
        ValueError: If role is invalid
        mysql.connector.Error: If DB error (e.g., duplicate username)
    """
    # 🔒 Validate role before DB operation
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role '{role}'. Must be one of: {VALID_ROLES}")
    
    # 🔒 Hash password before storing
    password_hash = hash_password(password_plaintext)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query to prevent injection
        query = """
            INSERT INTO users (username, email, password_hash, role, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (username, email, password_hash, role))
        conn.commit()
        
        # Retrieve and return created user
        return get_user_by_username(username)
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email: str):
    """
    Retrieve user by email
    Useful for registration uniqueness check
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT id, uuid, username, email, password_hash, role, created_at, updated_at FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row[0],
                uuid=row[1],
                username=row[2],
                email=row[3],
                password_hash=row[4],
                role=row[5],
                created_at=row[6],
                updated_at=row[7]
            )
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_id_by_uuid(user_uuid: str) -> int | None:
    """
    Gets USER ID for internal transactions
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT id FROM users WHERE uuid = %s"
        cursor.execute(query, (user_uuid,))
        user = cursor.fetchone()
        return user["id"] if user else None
    finally:
        cursor.close()
        conn.close()
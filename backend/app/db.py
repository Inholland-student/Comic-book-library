"""
Database abstraction layer for Comic Library
🔒 Security: Parameterized queries prevent SQL injection
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from app.config import Config
from app.models import User, Comic, VALID_ROLES
import bcrypt


def get_connection():
    """
    Create and return a MySQL database connection
    Uses connection config from Config
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise


def hash_password(plaintext: str) -> str:
    """
    🔒 Hash password using bcrypt
    Cost factor 12 makes it slow to resist brute force
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plaintext.encode('utf-8'), salt).decode('utf-8')


def verify_password(plaintext: str, hash_value: str) -> bool:
    """
    🔒 Verify plaintext password against bcrypt hash
    """
    return bcrypt.checkpw(plaintext.encode('utf-8'), hash_value.encode('utf-8'))


# ============================================================================
# USER OPERATIONS
# ============================================================================

def get_user_by_username(username: str):
    """
    Retrieve user by username
    Returns User object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query prevents SQL injection
        query = "SELECT id, username, email, password_hash, role, created_at, updated_at FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_by_id(user_id: int):
    """
    Retrieve user by ID
    Returns User object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query
        query = "SELECT id, username, email, password_hash, role, created_at, updated_at FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                created_at=row[5],
                updated_at=row[6]
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
        query = "SELECT id, username, email, password_hash, role, created_at, updated_at FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                password_hash=row[3],
                role=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
        return None
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# COMIC OPERATIONS
# ============================================================================

def get_all_comics():
    """
    Retrieve all comics from database
    Returns list of Comic objects
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT id, serie, number, title, created_by, created_at, updated_at FROM comics ORDER BY created_at DESC"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        comics = []
        for row in rows:
            comic = Comic(
                id=row[0],
                serie=row[1],
                number=row[2],
                title=row[3],
                created_by=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
            comics.append(comic)
        return comics
    finally:
        cursor.close()
        conn.close()


def get_comic_by_id(comic_id: int):
    """
    Retrieve comic by ID
    Returns Comic object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query
        query = "SELECT id, serie, number, title, created_by, created_at, updated_at FROM comics WHERE id = %s"
        cursor.execute(query, (comic_id,))
        row = cursor.fetchone()
        
        if row:
            return Comic(
                id=row[0],
                serie=row[1],
                number=row[2],
                title=row[3],
                created_by=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
        return None
    finally:
        cursor.close()
        conn.close()


def create_comic(serie: str, number: str, title: str, created_by: int):
    """
    Create a new comic
    
    Args:
        serie: Comic series name
        number: Issue number
        title: Comic title
        created_by: User ID of creator (must be admin)
    
    Returns:
        Comic object if created successfully
    
    Raises:
        mysql.connector.Error: If DB error (e.g., invalid created_by FK)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query to prevent injection
        query = """
            INSERT INTO comics (serie, number, title, created_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (serie, number, title, created_by))
        conn.commit()
        
        # Get the ID of inserted comic
        comic_id = cursor.lastrowid
        return get_comic_by_id(comic_id)
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def update_comic(comic_id: int, serie: str, number: str, title: str):
    """
    Update a comic
    
    Args:
        comic_id: ID of comic to update
        serie: New series name
        number: New issue number
        title: New title
    
    Returns:
        Updated Comic object
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query
        query = """
            UPDATE comics 
            SET serie = %s, number = %s, title = %s, updated_at = NOW()
            WHERE id = %s
        """
        cursor.execute(query, (serie, number, title, comic_id))
        conn.commit()
        
        return get_comic_by_id(comic_id)
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def delete_comic(comic_id: int):
    """
    Delete a comic by ID
    
    Args:
        comic_id: ID of comic to delete
    
    Raises:
        mysql.connector.Error: If DB error
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 🔒 Parameterized query
        query = "DELETE FROM comics WHERE id = %s"
        cursor.execute(query, (comic_id,))
        conn.commit()
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

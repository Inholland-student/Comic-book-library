from app.features.common.persistence.db import get_connection
from .comic import Comic
from mysql.connector import Error

def get_all_comics():
    """
    Retrieve all comics from database
    Returns list of Comic objects
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = "SELECT c.id, c.serie, c.number, c.title, u.uuid, c.created_at, c.updated_at FROM comics c JOIN users u ON c.created_by = u.id ORDER BY c.created_at DESC"
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


def count_comics() -> int:
    """
    Return total number of comics.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM comics")
        row = cursor.fetchone()
        return int(row[0]) if row else 0
    finally:
        cursor.close()
        conn.close()


def get_comics_page(limit: int, offset: int):
    """
    Retrieve a paginated slice of comics.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT c.id, c.serie, c.number, c.title, u.uuid, c.created_at, c.updated_at
            FROM comics c
            JOIN users u ON c.created_by = u.id
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()

        comics = []
        for row in rows:
            comics.append(Comic(
                id=row[0],
                serie=row[1],
                number=row[2],
                title=row[3],
                created_by=row[4],
                created_at=row[5],
                updated_at=row[6]
            ))
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
        query = "SELECT c.id, c.serie, c.number, c.title, u.uuid, c.created_at, c.updated_at FROM comics c JOIN users u ON c.created_by = u.id WHERE c.id = %s"
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

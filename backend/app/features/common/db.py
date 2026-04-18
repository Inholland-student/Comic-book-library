"""
Database abstraction layer for Comic Library
🔒 Security: Parameterized queries prevent SQL injection
"""
import mysql.connector
from mysql.connector import Error
from app.config import Config

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
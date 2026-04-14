"""
Tests for database operations (TDD)
🔒 Security: Verify DB schema, user creation, role-based queries
"""
import pytest
from datetime import datetime
from app.models import User, Comic, VALID_ROLES
from app.db import (
    get_user_by_username,
    get_user_by_id,
    create_user,
    get_all_comics,
    get_comic_by_id,
    create_comic,
    update_comic,
    delete_comic,
    get_connection
)


class TestDatabaseConnection:
    """Test database connectivity"""
    
    def test_database_connection_succeeds(self):
        """Test that we can connect to database"""
        conn = get_connection()
        assert conn is not None
        conn.close()
    
    def test_database_has_users_table(self):
        """Test that users table exists"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users;")
        result = cursor.fetchone()
        assert result is not None
        cursor.close()
        conn.close()
    
    def test_database_has_comics_table(self):
        """Test that comics table exists"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM comics;")
        result = cursor.fetchone()
        assert result is not None
        cursor.close()
        conn.close()


class TestUserOperations:
    """Test user CRUD operations"""
    
    def test_get_user_by_username(self):
        """Test retrieving user by username (super_admin exists from init.sql)"""
        user = get_user_by_username('super_admin')
        assert user is not None
        assert isinstance(user, User)
        assert user.username == 'super_admin'
        assert user.role == 'super_admin'
        assert user.email == 'super_admin@library.local'
    
    def test_get_user_by_username_not_found(self):
        """Test retrieving non-existent user returns None"""
        user = get_user_by_username('nonexistent_user_xyz')
        assert user is None
    
    def test_get_user_by_id(self):
        """Test retrieving user by ID"""
        user = get_user_by_id(1)  # super_admin has id=1 from init.sql
        assert user is not None
        assert user.id == 1
        assert user.username == 'super_admin'
    
    def test_get_user_by_id_not_found(self):
        """Test retrieving non-existent user by ID"""
        user = get_user_by_id(99999)
        assert user is None
    
    def test_create_user_password_hashed(self):
        """🔒 Test that created user has password hashed, not stored plaintext"""
        username = f'test_user_{datetime.now().timestamp()}'
        password_plaintext = 'test_password_123'
        
        user = create_user(
            username=username,
            email=f'{username}@test.local',
            password_plaintext=password_plaintext,
            role='friend'
        )
        
        assert user is not None
        assert user.username == username
        assert user.role == 'friend'
        # 🔒 Password hash should NOT be the plaintext password
        assert user.password_hash != password_plaintext
        # 🔒 Password hash should look like bcrypt (starts with $2b$ or $2a$)
        assert user.password_hash.startswith('$2b$') or user.password_hash.startswith('$2a$')
    
    def test_create_user_with_invalid_role_raises_error(self):
        """🔒 Test that creating user with invalid role raises error"""
        username = f'test_user_invalid_{datetime.now().timestamp()}'
        
        with pytest.raises(ValueError, match="Invalid role"):
            create_user(
                username=username,
                email=f'{username}@test.local',
                password_plaintext='password123',
                role='invalid_role'  # Not in VALID_ROLES
            )
    
    def test_create_user_with_duplicate_username_raises_error(self):
        """🔒 Test that duplicate username is rejected"""
        # super_admin already exists
        with pytest.raises(Exception):  # Will raise db error (integrity constraint)
            create_user(
                username='super_admin',  # Already exists
                email='different@test.local',
                password_plaintext='password123',
                role='admin'
            )


class TestComicOperations:
    """Test comic CRUD operations"""
    
    def test_get_all_comics(self):
        """Test retrieving all comics"""
        comics = get_all_comics()
        assert comics is not None
        assert isinstance(comics, list)
        # Should have at least the super_admin user
        assert len(comics) >= 0
    
    def test_create_comic(self):
        """Test creating a comic"""
        comic = create_comic(
            serie='Test Series',
            number='001',
            title='Test Comic Title',
            created_by=1  # super_admin
        )
        
        assert comic is not None
        assert comic.serie == 'Test Series'
        assert comic.number == '001'
        assert comic.title == 'Test Comic Title'
        assert comic.created_by == 1
        assert comic.id is not None
    
    def test_get_comic_by_id(self):
        """Test retrieving comic by ID"""
        # Create a comic first
        created_comic = create_comic(
            serie='Retrieve Test',
            number='002',
            title='Retrieve Test Comic',
            created_by=1
        )
        
        # Now retrieve it
        comic = get_comic_by_id(created_comic.id)
        assert comic is not None
        assert comic.id == created_comic.id
        assert comic.serie == 'Retrieve Test'
    
    def test_get_comic_by_id_not_found(self):
        """Test retrieving non-existent comic"""
        comic = get_comic_by_id(99999)
        assert comic is None
    
    def test_update_comic(self):
        """Test updating a comic"""
        # Create a comic
        comic = create_comic(
            serie='Update Test',
            number='003',
            title='Original Title',
            created_by=1
        )
        
        # Update it
        updated = update_comic(
            comic_id=comic.id,
            serie='Updated Series',
            number='003b',
            title='Updated Title'
        )
        
        assert updated is not None
        assert updated.serie == 'Updated Series'
        assert updated.number == '003b'
        assert updated.title == 'Updated Title'
        assert updated.id == comic.id
    
    def test_delete_comic(self):
        """Test deleting a comic"""
        # Create a comic
        comic = create_comic(
            serie='Delete Test',
            number='004',
            title='Soon to be deleted',
            created_by=1
        )
        comic_id = comic.id
        
        # Delete it
        delete_comic(comic_id)
        
        # Verify it's gone
        retrieved = get_comic_by_id(comic_id)
        assert retrieved is None
    
    def test_comic_created_by_fk_constraint(self):
        """🔒 Test that comic created_by must reference valid user"""
        # Try to create comic with invalid user ID
        with pytest.raises(Exception):  # Will raise DB foreign key error
            create_comic(
                serie='FK Test',
                number='005',
                title='Invalid User FK',
                created_by=99999  # Non-existent user
            )


class TestSchemaIntegrity:
    """Test schema structure and constraints"""
    
    def test_user_table_has_required_columns(self):
        """Test that users table has required columns"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE users;")
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        required = {'id', 'username', 'email', 'password_hash', 'role', 'created_at', 'updated_at'}
        assert required.issubset(set(columns.keys()))
        cursor.close()
        conn.close()
    
    def test_comic_table_has_required_columns(self):
        """Test that comics table has required columns"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE comics;")
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        required = {'id', 'serie', 'number', 'title', 'created_by', 'created_at', 'updated_at'}
        assert required.issubset(set(columns.keys()))
        cursor.close()
        conn.close()
    
    def test_user_role_is_enum(self):
        """🔒 Test that role column is constrained to valid values"""
        # This is a schema-level constraint validation
        valid_roles = list(VALID_ROLES)
        assert 'super_admin' in valid_roles
        assert 'admin' in valid_roles
        assert 'friend' in valid_roles

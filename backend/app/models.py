"""
Data models for Comic Library application
Represents users and comics with proper typing
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model with role-based access control"""
    id: int
    uuid: str
    username: str
    email: str
    password_hash: str
    role: str  # super_admin, admin, friend
    created_at: datetime
    updated_at: datetime
    
    def __repr__(self):
        """Mask password hash in string representation for security"""
        return f"<User id={self.id} username={self.username} role={self.role}>"


@dataclass
class Comic:
    """Comic book model"""
    id: int
    serie: str
    number: str
    title: str
    created_by: str  # FK to User.uuid
    created_at: datetime
    updated_at: datetime


# Schema validation
VALID_ROLES = {'super_admin', 'admin', 'friend'}

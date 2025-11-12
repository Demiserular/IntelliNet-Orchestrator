"""User model for authentication and authorization"""

from enum import Enum
from typing import Optional
from datetime import datetime


class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"


class User:
    """User model with authentication and role information"""
    
    def __init__(
        self,
        username: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        disabled: bool = False,
        created_at: Optional[datetime] = None
    ):
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
        self.email = email
        self.full_name = full_name
        self.disabled = disabled
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            "username": self.username,
            "role": self.role.value,
            "email": self.email,
            "full_name": self.full_name,
            "disabled": self.disabled,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN

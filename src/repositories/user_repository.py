"""User repository for managing user data in SQLite"""

import sqlite3
from typing import Optional, List
from src.models.user import User, UserRole
from datetime import datetime


class UserRepository:
    """Repository for user data persistence"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self._initialize_schema()
        self._create_default_users()
    
    def _initialize_schema(self):
        """Create users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            disabled INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def _create_default_users(self):
        """Create default admin and user accounts if they don't exist"""
        from src.services.auth_service import AuthService
        
        auth_service = AuthService()
        
        # Check if admin exists
        if not self.get_user("admin"):
            admin = User(
                username="admin",
                hashed_password=auth_service.get_password_hash("admin123"),
                role=UserRole.ADMIN,
                email="admin@intellinet.com",
                full_name="System Administrator"
            )
            self.create_user(admin)
        
        # Check if regular user exists
        if not self.get_user("user"):
            user = User(
                username="user",
                hashed_password=auth_service.get_password_hash("user123"),
                role=UserRole.USER,
                email="user@intellinet.com",
                full_name="Regular User"
            )
            self.create_user(user)
    
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO users (username, hashed_password, role, email, full_name, disabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user.username,
                user.hashed_password,
                user.role.value,
                user.email,
                user.full_name,
                1 if user.disabled else 0,
                user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT username, hashed_password, role, email, full_name, disabled, created_at
        FROM users
        WHERE username = ?
        """, (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            username=row[0],
            hashed_password=row[1],
            role=UserRole(row[2]),
            email=row[3],
            full_name=row[4],
            disabled=bool(row[5]),
            created_at=datetime.fromisoformat(row[6]) if row[6] else None
        )
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT username, hashed_password, role, email, full_name, disabled, created_at
        FROM users
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append(User(
                username=row[0],
                hashed_password=row[1],
                role=UserRole(row[2]),
                email=row[3],
                full_name=row[4],
                disabled=bool(row[5]),
                created_at=datetime.fromisoformat(row[6]) if row[6] else None
            ))
        
        conn.close()
        return users
    
    def update_user(self, user: User) -> bool:
        """Update an existing user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE users
        SET hashed_password = ?, role = ?, email = ?, full_name = ?, disabled = ?
        WHERE username = ?
        """, (
            user.hashed_password,
            user.role.value,
            user.email,
            user.full_name,
            1 if user.disabled else 0,
            user.username
        ))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def get_users_dict(self) -> dict[str, User]:
        """Get all users as a dictionary (username -> User)"""
        users = self.get_all_users()
        return {user.username: user for user in users}

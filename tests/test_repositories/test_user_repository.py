"""Tests for user repository"""

import pytest
import os
from src.repositories.user_repository import UserRepository
from src.models.user import User, UserRole
from src.services.auth_service import AuthService


class TestUserRepository:
    """Test suite for UserRepository"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Use in-memory database for testing
        self.repo = UserRepository(db_path=":memory:")
        self.auth_service = AuthService()
    
    def test_default_users_created(self):
        """Test that default admin and user accounts are created"""
        admin = self.repo.get_user("admin")
        user = self.repo.get_user("user")
        
        assert admin is not None
        assert admin.role == UserRole.ADMIN
        assert user is not None
        assert user.role == UserRole.USER
    
    def test_create_user(self):
        """Test creating a new user"""
        new_user = User(
            username="testuser",
            hashed_password=self.auth_service.get_password_hash("password123"),
            role=UserRole.USER,
            email="test@example.com",
            full_name="Test User"
        )
        
        success = self.repo.create_user(new_user)
        assert success
        
        # Verify user was created
        retrieved = self.repo.get_user("testuser")
        assert retrieved is not None
        assert retrieved.username == "testuser"
        assert retrieved.email == "test@example.com"
        assert retrieved.role == UserRole.USER
    
    def test_create_duplicate_user(self):
        """Test that creating duplicate user fails"""
        user1 = User(
            username="duplicate",
            hashed_password=self.auth_service.get_password_hash("password"),
            role=UserRole.USER
        )
        
        success1 = self.repo.create_user(user1)
        assert success1
        
        # Try to create user with same username
        user2 = User(
            username="duplicate",
            hashed_password=self.auth_service.get_password_hash("password2"),
            role=UserRole.ADMIN
        )
        
        success2 = self.repo.create_user(user2)
        assert not success2
    
    def test_get_nonexistent_user(self):
        """Test getting a user that doesn't exist"""
        user = self.repo.get_user("nonexistent")
        assert user is None
    
    def test_get_all_users(self):
        """Test getting all users"""
        users = self.repo.get_all_users()
        
        # Should have at least the default admin and user
        assert len(users) >= 2
        
        usernames = [u.username for u in users]
        assert "admin" in usernames
        assert "user" in usernames
    
    def test_update_user(self):
        """Test updating a user"""
        # Get existing user
        user = self.repo.get_user("admin")
        assert user is not None
        
        # Update user properties
        user.email = "newemail@example.com"
        user.full_name = "Updated Admin"
        
        success = self.repo.update_user(user)
        assert success
        
        # Verify update
        updated = self.repo.get_user("admin")
        assert updated.email == "newemail@example.com"
        assert updated.full_name == "Updated Admin"
    
    def test_update_nonexistent_user(self):
        """Test updating a user that doesn't exist"""
        user = User(
            username="nonexistent",
            hashed_password="hash",
            role=UserRole.USER
        )
        
        success = self.repo.update_user(user)
        assert not success
    
    def test_delete_user(self):
        """Test deleting a user"""
        # Create a user to delete
        user = User(
            username="todelete",
            hashed_password=self.auth_service.get_password_hash("password"),
            role=UserRole.USER
        )
        
        self.repo.create_user(user)
        
        # Verify user exists
        assert self.repo.get_user("todelete") is not None
        
        # Delete user
        success = self.repo.delete_user("todelete")
        assert success
        
        # Verify user is deleted
        assert self.repo.get_user("todelete") is None
    
    def test_delete_nonexistent_user(self):
        """Test deleting a user that doesn't exist"""
        success = self.repo.delete_user("nonexistent")
        assert not success
    
    def test_get_users_dict(self):
        """Test getting users as dictionary"""
        users_dict = self.repo.get_users_dict()
        
        assert isinstance(users_dict, dict)
        assert "admin" in users_dict
        assert "user" in users_dict
        
        assert isinstance(users_dict["admin"], User)
        assert users_dict["admin"].role == UserRole.ADMIN
    
    def test_disabled_user_flag(self):
        """Test disabled user flag"""
        # Create disabled user
        disabled_user = User(
            username="disabled",
            hashed_password=self.auth_service.get_password_hash("password"),
            role=UserRole.USER,
            disabled=True
        )
        
        self.repo.create_user(disabled_user)
        
        # Retrieve and verify
        retrieved = self.repo.get_user("disabled")
        assert retrieved is not None
        assert retrieved.disabled is True
    
    def test_user_role_persistence(self):
        """Test that user roles are persisted correctly"""
        # Create admin user
        admin = User(
            username="testadmin",
            hashed_password=self.auth_service.get_password_hash("password"),
            role=UserRole.ADMIN
        )
        
        self.repo.create_user(admin)
        
        # Retrieve and verify role
        retrieved = self.repo.get_user("testadmin")
        assert retrieved.role == UserRole.ADMIN
        assert retrieved.is_admin()
    
    def test_password_hash_stored(self):
        """Test that password hash is stored, not plain password"""
        password = "mypassword123"
        user = User(
            username="hashtest",
            hashed_password=self.auth_service.get_password_hash(password),
            role=UserRole.USER
        )
        
        self.repo.create_user(user)
        
        # Retrieve user
        retrieved = self.repo.get_user("hashtest")
        
        # Hash should not equal plain password
        assert retrieved.hashed_password != password
        
        # But should verify correctly
        assert self.auth_service.verify_password(password, retrieved.hashed_password)

"""Tests for User model"""

import pytest
from datetime import datetime
from src.models.user import User, UserRole


class TestUser:
    """Test suite for User model"""
    
    def test_user_creation(self):
        """Test creating a user"""
        user = User(
            username="testuser",
            hashed_password="hashed_password",
            role=UserRole.USER,
            email="test@example.com",
            full_name="Test User"
        )
        
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"
        assert user.role == UserRole.USER
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.disabled is False
        assert isinstance(user.created_at, datetime)
    
    def test_user_with_admin_role(self):
        """Test creating a user with admin role"""
        admin = User(
            username="admin",
            hashed_password="hashed_password",
            role=UserRole.ADMIN
        )
        
        assert admin.role == UserRole.ADMIN
        assert admin.is_admin()
    
    def test_user_with_user_role(self):
        """Test creating a user with regular user role"""
        user = User(
            username="user",
            hashed_password="hashed_password",
            role=UserRole.USER
        )
        
        assert user.role == UserRole.USER
        assert not user.is_admin()
    
    def test_disabled_user(self):
        """Test creating a disabled user"""
        user = User(
            username="disabled",
            hashed_password="hashed_password",
            role=UserRole.USER,
            disabled=True
        )
        
        assert user.disabled is True
    
    def test_user_to_dict(self):
        """Test converting user to dictionary"""
        user = User(
            username="testuser",
            hashed_password="hashed_password",
            role=UserRole.USER,
            email="test@example.com",
            full_name="Test User"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict["username"] == "testuser"
        assert user_dict["role"] == "user"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["full_name"] == "Test User"
        assert user_dict["disabled"] is False
        
        # Password should not be in dictionary
        assert "hashed_password" not in user_dict
        assert "password" not in user_dict
    
    def test_user_role_enum(self):
        """Test UserRole enum values"""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.USER.value == "user"
    
    def test_is_admin_method(self):
        """Test is_admin method"""
        admin = User(
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN
        )
        
        user = User(
            username="user",
            hashed_password="hash",
            role=UserRole.USER
        )
        
        assert admin.is_admin() is True
        assert user.is_admin() is False
    
    def test_user_default_values(self):
        """Test user default values"""
        user = User(
            username="testuser",
            hashed_password="hash",
            role=UserRole.USER
        )
        
        # Default values
        assert user.email is None
        assert user.full_name is None
        assert user.disabled is False
        assert user.created_at is not None
    
    def test_user_with_custom_created_at(self):
        """Test user with custom created_at timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        
        user = User(
            username="testuser",
            hashed_password="hash",
            role=UserRole.USER,
            created_at=custom_time
        )
        
        assert user.created_at == custom_time

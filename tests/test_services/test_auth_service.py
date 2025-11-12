"""Tests for authentication service"""

import pytest
from datetime import timedelta
from src.services.auth_service import AuthService
from src.models.user import User, UserRole


class TestAuthService:
    """Test suite for AuthService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.auth_service = AuthService(secret_key="test-secret-key")
        
        # Create test users
        self.admin_user = User(
            username="admin",
            hashed_password=self.auth_service.get_password_hash("admin123"),
            role=UserRole.ADMIN,
            email="admin@test.com"
        )
        
        self.regular_user = User(
            username="user",
            hashed_password=self.auth_service.get_password_hash("user123"),
            role=UserRole.USER,
            email="user@test.com"
        )
        
        self.disabled_user = User(
            username="disabled",
            hashed_password=self.auth_service.get_password_hash("disabled123"),
            role=UserRole.USER,
            disabled=True
        )
        
        self.user_db = {
            "admin": self.admin_user,
            "user": self.regular_user,
            "disabled": self.disabled_user
        }
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        password = "test_password_123"
        hashed = self.auth_service.get_password_hash(password)
        
        # Hash should not equal plain password
        assert hashed != password
        
        # Should be able to verify correct password
        assert self.auth_service.verify_password(password, hashed)
        
        # Should not verify incorrect password
        assert not self.auth_service.verify_password("wrong_password", hashed)
    
    def test_create_access_token(self):
        """Test JWT token generation"""
        token = self.auth_service.create_access_token(
            username="testuser",
            role=UserRole.ADMIN
        )
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding a valid JWT token"""
        username = "testuser"
        role = UserRole.ADMIN
        
        token = self.auth_service.create_access_token(username=username, role=role)
        payload = self.auth_service.decode_token(token)
        
        # Payload should contain username and role
        assert payload is not None
        assert payload["sub"] == username
        assert payload["role"] == role.value
        assert "exp" in payload
    
    def test_decode_invalid_token(self):
        """Test decoding an invalid JWT token"""
        invalid_token = "invalid.token.here"
        payload = self.auth_service.decode_token(invalid_token)
        
        # Should return None for invalid token
        assert payload is None
    
    def test_decode_expired_token(self):
        """Test decoding an expired JWT token"""
        # Create token with negative expiration (already expired)
        token = self.auth_service.create_access_token(
            username="testuser",
            role=UserRole.USER,
            expires_delta=timedelta(seconds=-1)
        )
        
        payload = self.auth_service.decode_token(token)
        
        # Should return None for expired token
        assert payload is None
    
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        user = self.auth_service.authenticate_user(
            username="admin",
            password="admin123",
            user_db=self.user_db
        )
        
        assert user is not None
        assert user.username == "admin"
        assert user.role == UserRole.ADMIN
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        user = self.auth_service.authenticate_user(
            username="admin",
            password="wrong_password",
            user_db=self.user_db
        )
        
        assert user is None
    
    def test_authenticate_user_nonexistent(self):
        """Test authentication with nonexistent user"""
        user = self.auth_service.authenticate_user(
            username="nonexistent",
            password="password",
            user_db=self.user_db
        )
        
        assert user is None
    
    def test_authenticate_disabled_user(self):
        """Test authentication with disabled user"""
        user = self.auth_service.authenticate_user(
            username="disabled",
            password="disabled123",
            user_db=self.user_db
        )
        
        assert user is None
    
    def test_token_contains_role(self):
        """Test that JWT token contains user role"""
        admin_token = self.auth_service.create_access_token(
            username="admin",
            role=UserRole.ADMIN
        )
        
        user_token = self.auth_service.create_access_token(
            username="user",
            role=UserRole.USER
        )
        
        admin_payload = self.auth_service.decode_token(admin_token)
        user_payload = self.auth_service.decode_token(user_token)
        
        assert admin_payload["role"] == "admin"
        assert user_payload["role"] == "user"
    
    def test_different_tokens_for_different_users(self):
        """Test that different users get different tokens"""
        token1 = self.auth_service.create_access_token(
            username="user1",
            role=UserRole.USER
        )
        
        token2 = self.auth_service.create_access_token(
            username="user2",
            role=UserRole.USER
        )
        
        # Tokens should be different
        assert token1 != token2
        
        # But both should be valid
        payload1 = self.auth_service.decode_token(token1)
        payload2 = self.auth_service.decode_token(token2)
        
        assert payload1 is not None
        assert payload2 is not None
        assert payload1["sub"] == "user1"
        assert payload2["sub"] == "user2"

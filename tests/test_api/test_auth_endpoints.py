"""Tests for authentication API endpoints"""

import pytest
from httpx import AsyncClient
from src.api.app import app
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    """Create auth service for testing"""
    return AuthService(secret_key="test-secret-key")


@pytest.fixture
def user_repo():
    """Create user repository for testing"""
    return UserRepository(db_path=":memory:")


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    async def test_login_success(self):
        """Test successful login"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "admin",
                    "password": "admin123"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    async def test_login_wrong_password(self):
        """Test login with wrong password"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "admin",
                    "password": "wrong_password"
                }
            )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "username": "nonexistent",
                    "password": "password"
                }
            )
        
        assert response.status_code == 401
    
    async def test_get_current_user_with_valid_token(self):
        """Test getting current user with valid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First login to get token
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "username": "admin",
                    "password": "admin123"
                }
            )
            
            token = login_response.json()["access_token"]
            
            # Then get current user
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    async def test_get_current_user_without_token(self):
        """Test getting current user without token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    async def test_get_current_user_with_invalid_token(self):
        """Test getting current user with invalid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer invalid_token"}
            )
        
        assert response.status_code == 401
    
    async def test_oauth2_token_endpoint(self):
        """Test OAuth2 compatible token endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/token",
                data={
                    "username": "admin",
                    "password": "admin123"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
class TestRoleBasedAuthorization:
    """Test suite for role-based authorization"""
    
    async def get_admin_token(self) -> str:
        """Helper to get admin token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            return response.json()["access_token"]
    
    async def get_user_token(self) -> str:
        """Helper to get regular user token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/auth/login",
                json={"username": "user", "password": "user123"}
            )
            return response.json()["access_token"]
    
    async def test_admin_can_create_device(self):
        """Test that admin can create devices"""
        token = await self.get_admin_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/topology/device",
                json={
                    "id": "TEST_DEVICE",
                    "name": "Test Device",
                    "type": "MPLS",
                    "capacity": 100.0
                },
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Admin should be able to create device (201 or 409 if exists)
        assert response.status_code in [201, 409]
    
    async def test_user_cannot_create_device(self):
        """Test that regular user cannot create devices"""
        token = await self.get_user_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/topology/device",
                json={
                    "id": "TEST_DEVICE_2",
                    "name": "Test Device 2",
                    "type": "MPLS",
                    "capacity": 100.0
                },
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Regular user should get 403 Forbidden
        assert response.status_code == 403
    
    async def test_user_can_view_topology(self):
        """Test that regular user can view topology"""
        token = await self.get_user_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/topology/",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Regular user should be able to view topology
        assert response.status_code == 200
    
    async def test_user_can_provision_service(self):
        """Test that regular user can provision services"""
        token = await self.get_user_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/service/provision",
                json={
                    "id": "TEST_SERVICE",
                    "service_type": "MPLS_VPN",
                    "source_device_id": "R1",
                    "target_device_id": "R2",
                    "bandwidth": 10.0
                },
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # User should be able to provision (may fail for other reasons)
        # but should not get 403
        assert response.status_code != 403
    
    async def test_user_cannot_delete_device(self):
        """Test that regular user cannot delete devices"""
        token = await self.get_user_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/api/topology/device/TEST_DEVICE",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Regular user should get 403 Forbidden
        assert response.status_code == 403
    
    async def test_admin_can_delete_device(self):
        """Test that admin can delete devices"""
        token = await self.get_admin_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/api/topology/device/TEST_DEVICE",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Admin should be able to delete (200 or 404 if not exists)
        assert response.status_code in [200, 404]
    
    async def test_unauthenticated_request_rejected(self):
        """Test that unauthenticated requests are rejected"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/topology/")
        
        # Should get 401 Unauthorized
        assert response.status_code == 401
    
    async def test_user_cannot_decommission_service(self):
        """Test that regular user cannot decommission services"""
        token = await self.get_user_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/api/service/TEST_SERVICE",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Regular user should get 403 Forbidden
        assert response.status_code == 403
    
    async def test_admin_can_decommission_service(self):
        """Test that admin can decommission services"""
        token = await self.get_admin_token()
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                "/api/service/TEST_SERVICE",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Admin should be able to decommission (may fail if service doesn't exist)
        # but should not get 403
        assert response.status_code != 403


@pytest.mark.asyncio
class TestTokenExpiration:
    """Test suite for token expiration handling"""
    
    async def test_expired_token_rejected(self, auth_service):
        """Test that expired tokens are rejected"""
        from datetime import timedelta
        
        # Create an expired token
        expired_token = auth_service.create_access_token(
            username="admin",
            role="admin",
            expires_delta=timedelta(seconds=-1)
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {expired_token}"}
            )
        
        # Expired token should be rejected
        assert response.status_code == 401

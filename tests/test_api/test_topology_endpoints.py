"""Integration tests for topology management endpoints"""

import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_create_device_success(client):
    """Test successful device creation"""
    device_data = {
        "id": "R1",
        "name": "Core Router 1",
        "type": "MPLS",
        "capacity": 100.0,
        "location": "DataCenter-A"
    }
    
    response = client.post("/api/topology/device", json=device_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert "Device created successfully" in data["message"]
    assert data["data"]["id"] == "R1"


def test_create_device_invalid_type(client):
    """Test device creation with invalid type"""
    device_data = {
        "id": "R1",
        "name": "Core Router 1",
        "type": "INVALID_TYPE",
        "capacity": 100.0
    }
    
    response = client.post("/api/topology/device", json=device_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_DEVICE_TYPE"


def test_create_device_duplicate(client):
    """Test creating duplicate device"""
    device_data = {
        "id": "R1",
        "name": "Core Router 1",
        "type": "MPLS",
        "capacity": 100.0
    }
    
    # Create first device
    response = client.post("/api/topology/device", json=device_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Try to create duplicate
    response = client.post("/api/topology/device", json=device_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert data["error"]["code"] == "DEVICE_EXISTS"


def test_create_device_validation_error(client):
    """Test device creation with missing required fields"""
    device_data = {
        "id": "R1",
        "name": "Core Router 1"
        # Missing type and capacity
    }
    
    response = client.post("/api/topology/device", json=device_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_get_device_success(client):
    """Test getting a device"""
    # Create device first
    device_data = {
        "id": "R1",
        "name": "Core Router 1",
        "type": "MPLS",
        "capacity": 100.0
    }
    client.post("/api/topology/device", json=device_data)
    
    # Get device
    response = client.get("/api/topology/device/R1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "R1"
    assert data["name"] == "Core Router 1"


def test_get_device_not_found(client):
    """Test getting non-existent device"""
    response = client.get("/api/topology/device/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"



def test_delete_device_success(client):
    """Test successful device deletion"""
    # Create device first
    device_data = {
        "id": "R1",
        "name": "Core Router 1",
        "type": "MPLS",
        "capacity": 100.0
    }
    client.post("/api/topology/device", json=device_data)
    
    # Delete device
    response = client.delete("/api/topology/device/R1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "deleted successfully" in data["message"]


def test_delete_device_not_found(client):
    """Test deleting non-existent device"""
    response = client.delete("/api/topology/device/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"


def test_create_link_success(client):
    """Test successful link creation"""
    # Create devices first
    device1 = {
        "id": "R1",
        "name": "Router 1",
        "type": "MPLS",
        "capacity": 100.0
    }
    device2 = {
        "id": "R2",
        "name": "Router 2",
        "type": "MPLS",
        "capacity": 100.0
    }
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    # Create link
    link_data = {
        "id": "L1",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 10.0,
        "type": "fiber",
        "latency": 5.0
    }
    
    response = client.post("/api/topology/link", json=link_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert "Link created successfully" in data["message"]


def test_create_link_source_not_found(client):
    """Test link creation with non-existent source device"""
    link_data = {
        "id": "L1",
        "source_device_id": "NONEXISTENT",
        "target_device_id": "R2",
        "bandwidth": 10.0,
        "type": "fiber",
        "latency": 5.0
    }
    
    response = client.post("/api/topology/link", json=link_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"


def test_create_link_invalid_type(client):
    """Test link creation with invalid type"""
    # Create devices first
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    link_data = {
        "id": "L1",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 10.0,
        "type": "INVALID_TYPE",
        "latency": 5.0
    }
    
    response = client.post("/api/topology/link", json=link_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "INVALID_LINK_TYPE"


def test_get_topology(client):
    """Test getting complete topology"""
    # Create some devices and links
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    link_data = {
        "id": "L1",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 10.0,
        "type": "fiber",
        "latency": 5.0
    }
    client.post("/api/topology/link", json=link_data)
    
    # Get topology
    response = client.get("/api/topology/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "devices" in data
    assert "links" in data
    assert len(data["devices"]) == 2
    assert len(data["links"]) == 1

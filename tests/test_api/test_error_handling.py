"""Integration tests for error handling and response formats"""

import pytest
from fastapi import status


def test_validation_error_format(client):
    """Test that validation errors return standardized format"""
    # Send invalid request (missing required fields)
    response = client.post("/api/topology/device", json={"id": "R1"})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    
    # Check standardized error format
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_not_found_error_format(client):
    """Test that 404 errors return standardized format"""
    response = client.get("/api/topology/device/NONEXISTENT")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    
    # Check standardized error format
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "details" in data["error"]
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"


def test_conflict_error_format(client):
    """Test that conflict errors return standardized format"""
    device_data = {
        "id": "R1",
        "name": "Router 1",
        "type": "MPLS",
        "capacity": 100.0
    }
    
    # Create device
    client.post("/api/topology/device", json=device_data)
    
    # Try to create duplicate
    response = client.post("/api/topology/device", json=device_data)
    
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    
    # Check standardized error format
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert data["error"]["code"] == "DEVICE_EXISTS"


def test_success_response_format(client):
    """Test that success responses return standardized format"""
    device_data = {
        "id": "R1",
        "name": "Router 1",
        "type": "MPLS",
        "capacity": 100.0
    }
    
    response = client.post("/api/topology/device", json=device_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Check standardized success format
    assert "success" in data
    assert "message" in data
    assert data["success"] is True


def test_response_headers(client):
    """Test that responses include appropriate headers"""
    response = client.get("/health")
    
    # Check for process time header (added by logging middleware)
    assert "X-Process-Time" in response.headers


def test_cors_headers(client):
    """Test that CORS headers are present"""
    response = client.options("/api/topology/device")
    
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers or response.status_code == status.HTTP_200_OK


def test_invalid_json_format(client):
    """Test handling of invalid JSON"""
    response = client.post(
        "/api/topology/device",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    
    # Should return validation error
    assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]


def test_negative_capacity_validation(client):
    """Test validation of negative capacity"""
    device_data = {
        "id": "R1",
        "name": "Router 1",
        "type": "MPLS",
        "capacity": -100.0  # Invalid negative capacity
    }
    
    response = client.post("/api/topology/device", json=device_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_negative_bandwidth_validation(client):
    """Test validation of negative bandwidth"""
    # Create devices first
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    link_data = {
        "id": "L1",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": -10.0,  # Invalid negative bandwidth
        "type": "fiber"
    }
    
    response = client.post("/api/topology/link", json=link_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"

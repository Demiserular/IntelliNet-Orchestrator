"""Integration tests for service provisioning endpoints"""

import pytest
from fastapi import status


def test_provision_service_success(client):
    """Test successful service provisioning"""
    # Create devices first
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
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
    client.post("/api/topology/link", json=link_data)
    
    # Provision service
    service_data = {
        "id": "S1",
        "service_type": "MPLS_VPN",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 5.0,
        "latency_requirement": 10.0
    }
    
    response = client.post("/api/service/provision", json=service_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == "S1"
    assert data["service_type"] == "MPLS_VPN"
    assert data["status"] == "active"
    assert len(data["path"]) > 0


def test_provision_service_invalid_type(client):
    """Test service provisioning with invalid type"""
    service_data = {
        "id": "S1",
        "service_type": "INVALID_TYPE",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 5.0
    }
    
    response = client.post("/api/service/provision", json=service_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "INVALID_SERVICE_TYPE"


def test_provision_service_no_path(client):
    """Test service provisioning when no path exists"""
    # Create devices without connecting them
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    # Try to provision service
    service_data = {
        "id": "S1",
        "service_type": "MPLS_VPN",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 5.0
    }
    
    response = client.post("/api/service/provision", json=service_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "PROVISIONING_FAILED"


def test_provision_service_validation_error(client):
    """Test service provisioning with missing required fields"""
    service_data = {
        "id": "S1",
        "service_type": "MPLS_VPN"
        # Missing required fields
    }
    
    response = client.post("/api/service/provision", json=service_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_get_service_success(client, mock_neo4j_repo):
    """Test getting a service"""
    # Mock a service in the repository
    service_data = {
        "id": "S1",
        "service_type": "MPLS_VPN",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 5.0,
        "latency_requirement": 10.0,
        "status": "active",
        "path": ["R1", "R2"],
        "created_at": None,
        "activated_at": None
    }
    mock_neo4j_repo.services["S1"] = service_data
    
    # Get service
    response = client.get("/api/service/S1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "S1"
    assert data["service_type"] == "MPLS_VPN"


def test_get_service_not_found(client):
    """Test getting non-existent service"""
    response = client.get("/api/service/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "SERVICE_NOT_FOUND"


def test_decommission_service_success(client, mock_neo4j_repo):
    """Test successful service decommissioning"""
    # Mock a service in the repository
    service_data = {
        "id": "S1",
        "service_type": "MPLS_VPN",
        "source_device_id": "R1",
        "target_device_id": "R2",
        "bandwidth": 5.0,
        "latency_requirement": 10.0,
        "status": "active",
        "path": ["R1", "R2"],
        "created_at": None,
        "activated_at": None
    }
    mock_neo4j_repo.services["S1"] = service_data
    
    # Decommission service
    response = client.delete("/api/service/S1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_decommission_service_not_found(client):
    """Test decommissioning non-existent service"""
    response = client.delete("/api/service/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "SERVICE_NOT_FOUND"

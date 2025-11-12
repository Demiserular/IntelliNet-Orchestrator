"""Integration tests for analytics and optimization endpoints"""

import pytest
from fastapi import status


def test_get_analytics_status_empty(client):
    """Test analytics status with no devices"""
    response = client.get("/api/analytics/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_devices"] == 0
    assert data["active_devices"] == 0
    assert data["total_links"] == 0
    assert data["total_services"] == 0
    assert data["average_utilization"] == 0.0


def test_get_analytics_status_with_data(client):
    """Test analytics status with devices and links"""
    # Create devices
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
    
    # Get analytics
    response = client.get("/api/analytics/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_devices"] == 2
    assert data["active_devices"] == 2
    assert data["total_links"] == 1
    assert "average_utilization" in data


def test_find_optimal_path_success(client):
    """Test finding optimal path between devices"""
    # Create devices
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    # Find optimal path
    response = client.get("/api/optimization/path/R1/R2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["source"] == "R1"
    assert data["target"] == "R2"
    assert "path" in data
    assert len(data["path"]) > 0
    assert "total_latency" in data
    assert "available_bandwidth" in data


def test_find_optimal_path_source_not_found(client):
    """Test finding path with non-existent source"""
    response = client.get("/api/optimization/path/NONEXISTENT/R2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"


def test_find_optimal_path_target_not_found(client):
    """Test finding path with non-existent target"""
    # Create source device
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    
    response = client.get("/api/optimization/path/R1/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"


def test_find_optimal_path_no_path(client, mock_neo4j_repo):
    """Test finding path when no path exists"""
    # Create disconnected devices
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    device2 = {"id": "R2", "name": "Router 2", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    client.post("/api/topology/device", json=device2)
    
    # Mock no path found
    original_find = mock_neo4j_repo.find_optimal_path
    mock_neo4j_repo.find_optimal_path = lambda s, t: None
    
    response = client.get("/api/optimization/path/R1/R2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "PATH_NOT_FOUND"
    
    # Restore original method
    mock_neo4j_repo.find_optimal_path = original_find


def test_get_device_metrics_success(client, mock_metrics_repo):
    """Test getting device metrics"""
    # Create device
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    
    # Record some metrics
    mock_metrics_repo.record_device_metric("R1", 0.5, "active")
    mock_metrics_repo.record_device_metric("R1", 0.6, "active")
    
    # Get metrics
    response = client.get("/api/analytics/device/R1/metrics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["device_id"] == "R1"
    assert "metrics" in data
    assert len(data["metrics"]) >= 2


def test_get_device_metrics_not_found(client):
    """Test getting metrics for non-existent device"""
    response = client.get("/api/analytics/device/NONEXISTENT/metrics")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "DEVICE_NOT_FOUND"


def test_get_device_metrics_with_limit(client, mock_metrics_repo):
    """Test getting device metrics with limit parameter"""
    # Create device
    device1 = {"id": "R1", "name": "Router 1", "type": "MPLS", "capacity": 100.0}
    client.post("/api/topology/device", json=device1)
    
    # Record multiple metrics
    for i in range(10):
        mock_metrics_repo.record_device_metric("R1", 0.5 + i * 0.01, "active")
    
    # Get metrics with limit
    response = client.get("/api/analytics/device/R1/metrics?limit=5")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["metrics"]) <= 5

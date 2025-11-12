"""Unit tests for MetricsRepository"""

import pytest
import os
import tempfile
from datetime import datetime
from src.repositories.metrics_repository import MetricsRepository


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def metrics_repo(temp_db):
    """Create a MetricsRepository instance with temporary database"""
    return MetricsRepository(db_path=temp_db)


class TestMetricsRepositoryInitialization:
    """Test schema initialization"""
    
    def test_schema_initialization_creates_tables(self, temp_db):
        """Test that schema initialization creates all required tables"""
        repo = MetricsRepository(db_path=temp_db)
        
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Check device_metrics table exists
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='device_metrics'
        """)
        assert cursor.fetchone() is not None
        
        # Check link_metrics table exists
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='link_metrics'
        """)
        assert cursor.fetchone() is not None
        
        # Check service_logs table exists
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='service_logs'
        """)
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_schema_initialization_idempotent(self, temp_db):
        """Test that schema initialization can be called multiple times"""
        repo1 = MetricsRepository(db_path=temp_db)
        repo2 = MetricsRepository(db_path=temp_db)
        
        # Should not raise any errors
        assert repo1 is not None
        assert repo2 is not None


class TestDeviceMetrics:
    """Test device metrics recording and retrieval"""
    
    def test_record_device_metric(self, metrics_repo):
        """Test recording a device metric"""
        metrics_repo.record_device_metric("device1", 0.75, "active")
        
        # Verify the metric was recorded
        metrics = metrics_repo.get_device_metrics("device1")
        assert len(metrics) == 1
        assert metrics[0]["utilization"] == 0.75
        assert metrics[0]["status"] == "active"
    
    def test_record_multiple_device_metrics(self, metrics_repo):
        """Test recording multiple metrics for the same device"""
        metrics_repo.record_device_metric("device1", 0.50, "active")
        metrics_repo.record_device_metric("device1", 0.75, "active")
        metrics_repo.record_device_metric("device1", 0.90, "active")
        
        metrics = metrics_repo.get_device_metrics("device1")
        assert len(metrics) == 3
        # Verify all utilization values are present
        utilizations = [m["utilization"] for m in metrics]
        assert 0.50 in utilizations
        assert 0.75 in utilizations
        assert 0.90 in utilizations
    
    def test_get_device_metrics_with_limit(self, metrics_repo):
        """Test retrieving device metrics with limit parameter"""
        # Record 5 metrics
        for i in range(5):
            metrics_repo.record_device_metric("device1", i * 0.2, "active")
        
        # Get only 3 most recent
        metrics = metrics_repo.get_device_metrics("device1", limit=3)
        assert len(metrics) == 3
    
    def test_get_device_metrics_empty(self, metrics_repo):
        """Test retrieving metrics for non-existent device"""
        metrics = metrics_repo.get_device_metrics("nonexistent")
        assert len(metrics) == 0
    
    def test_device_metrics_different_devices(self, metrics_repo):
        """Test that metrics are isolated per device"""
        metrics_repo.record_device_metric("device1", 0.50, "active")
        metrics_repo.record_device_metric("device2", 0.75, "active")
        
        metrics1 = metrics_repo.get_device_metrics("device1")
        metrics2 = metrics_repo.get_device_metrics("device2")
        
        assert len(metrics1) == 1
        assert len(metrics2) == 1
        assert metrics1[0]["utilization"] == 0.50
        assert metrics2[0]["utilization"] == 0.75


class TestLinkMetrics:
    """Test link metrics recording and retrieval"""
    
    def test_record_link_metric(self, metrics_repo):
        """Test recording a link metric"""
        metrics_repo.record_link_metric("link1", 0.60, 5.5)
        
        metrics = metrics_repo.get_link_metrics("link1")
        assert len(metrics) == 1
        assert metrics[0]["utilization"] == 0.60
        assert metrics[0]["latency"] == 5.5
    
    def test_record_multiple_link_metrics(self, metrics_repo):
        """Test recording multiple metrics for the same link"""
        metrics_repo.record_link_metric("link1", 0.50, 5.0)
        metrics_repo.record_link_metric("link1", 0.75, 6.5)
        
        metrics = metrics_repo.get_link_metrics("link1")
        assert len(metrics) == 2
    
    def test_get_link_metrics_with_limit(self, metrics_repo):
        """Test retrieving link metrics with limit parameter"""
        for i in range(5):
            metrics_repo.record_link_metric("link1", i * 0.2, i * 1.0)
        
        metrics = metrics_repo.get_link_metrics("link1", limit=2)
        assert len(metrics) == 2
    
    def test_get_link_metrics_empty(self, metrics_repo):
        """Test retrieving metrics for non-existent link"""
        metrics = metrics_repo.get_link_metrics("nonexistent")
        assert len(metrics) == 0
    
    def test_link_metrics_different_links(self, metrics_repo):
        """Test that metrics are isolated per link"""
        metrics_repo.record_link_metric("link1", 0.50, 5.0)
        metrics_repo.record_link_metric("link2", 0.75, 10.0)
        
        metrics1 = metrics_repo.get_link_metrics("link1")
        metrics2 = metrics_repo.get_link_metrics("link2")
        
        assert len(metrics1) == 1
        assert len(metrics2) == 1
        assert metrics1[0]["latency"] == 5.0
        assert metrics2[0]["latency"] == 10.0


class TestServiceLogs:
    """Test service logs recording and retrieval"""
    
    def test_record_service_log(self, metrics_repo):
        """Test recording a service log"""
        metrics_repo.record_service_log("service1", "provisioned", "Service created successfully")
        
        logs = metrics_repo.get_service_logs("service1")
        assert len(logs) == 1
        assert logs[0]["event_type"] == "provisioned"
        assert logs[0]["details"] == "Service created successfully"
    
    def test_record_multiple_service_logs(self, metrics_repo):
        """Test recording multiple logs for the same service"""
        metrics_repo.record_service_log("service1", "provisioned", "Service created")
        metrics_repo.record_service_log("service1", "activated", "Service activated")
        metrics_repo.record_service_log("service1", "decommissioned", "Service removed")
        
        logs = metrics_repo.get_service_logs("service1")
        assert len(logs) == 3
    
    def test_get_service_logs_with_event_type_filter(self, metrics_repo):
        """Test retrieving service logs filtered by event type"""
        metrics_repo.record_service_log("service1", "provisioned", "Created")
        metrics_repo.record_service_log("service1", "failed", "Error occurred")
        metrics_repo.record_service_log("service1", "provisioned", "Recreated")
        
        # Get only 'provisioned' events
        logs = metrics_repo.get_service_logs("service1", event_type="provisioned")
        assert len(logs) == 2
        assert all(log["event_type"] == "provisioned" for log in logs)
        
        # Get only 'failed' events
        failed_logs = metrics_repo.get_service_logs("service1", event_type="failed")
        assert len(failed_logs) == 1
        assert failed_logs[0]["event_type"] == "failed"
    
    def test_get_service_logs_with_limit(self, metrics_repo):
        """Test retrieving service logs with limit parameter"""
        for i in range(5):
            metrics_repo.record_service_log("service1", "event", f"Event {i}")
        
        logs = metrics_repo.get_service_logs("service1", limit=3)
        assert len(logs) == 3
    
    def test_get_service_logs_empty(self, metrics_repo):
        """Test retrieving logs for non-existent service"""
        logs = metrics_repo.get_service_logs("nonexistent")
        assert len(logs) == 0
    
    def test_service_logs_different_services(self, metrics_repo):
        """Test that logs are isolated per service"""
        metrics_repo.record_service_log("service1", "provisioned", "Service 1 created")
        metrics_repo.record_service_log("service2", "provisioned", "Service 2 created")
        
        logs1 = metrics_repo.get_service_logs("service1")
        logs2 = metrics_repo.get_service_logs("service2")
        
        assert len(logs1) == 1
        assert len(logs2) == 1
        assert "Service 1" in logs1[0]["details"]
        assert "Service 2" in logs2[0]["details"]


class TestQueryFiltering:
    """Test advanced query filtering capabilities"""
    
    def test_link_metrics_time_range_filtering(self, metrics_repo):
        """Test link metrics retrieval with time range filtering"""
        # Record metrics at different times
        metrics_repo.record_link_metric("link1", 0.50, 5.0)
        
        # Get all metrics (no time filter)
        all_metrics = metrics_repo.get_link_metrics("link1")
        assert len(all_metrics) >= 1
        
        # Test with time range (should work with ISO format timestamps)
        # Note: In real usage, you'd pass actual timestamps
        metrics_with_range = metrics_repo.get_link_metrics(
            "link1", 
            start_time="2024-01-01 00:00:00",
            end_time="2025-12-31 23:59:59"
        )
        assert len(metrics_with_range) >= 1
    
    def test_combined_filters(self, metrics_repo):
        """Test combining multiple filters"""
        # Record various service logs
        metrics_repo.record_service_log("service1", "provisioned", "Event 1")
        metrics_repo.record_service_log("service1", "failed", "Event 2")
        metrics_repo.record_service_log("service1", "provisioned", "Event 3")
        metrics_repo.record_service_log("service1", "provisioned", "Event 4")
        
        # Filter by event type and limit
        logs = metrics_repo.get_service_logs("service1", event_type="provisioned", limit=2)
        assert len(logs) == 2
        assert all(log["event_type"] == "provisioned" for log in logs)


class TestRepositoryClose:
    """Test repository cleanup"""
    
    def test_close_method(self, metrics_repo):
        """Test that close method can be called without errors"""
        metrics_repo.close()
        # Should not raise any errors
        assert True

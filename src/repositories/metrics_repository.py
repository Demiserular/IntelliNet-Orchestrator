"""SQLite repository for metrics and logs storage"""

import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime


class MetricsRepository:
    """Repository for metrics and logs in SQLite"""
    
    def __init__(self, db_path: str = "metrics.db"):
        """
        Initialize MetricsRepository with SQLite connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create tables for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create device_metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            utilization REAL,
            status TEXT
        )
        """)
        
        # Create link_metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS link_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            utilization REAL,
            latency REAL
        )
        """)
        
        # Create service_logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            details TEXT
        )
        """)
        
        conn.commit()
        conn.close()
    
    def record_device_metric(self, device_id: str, utilization: float, status: str):
        """
        Record device utilization metric
        
        Args:
            device_id: Unique identifier for the device
            utilization: Current utilization percentage (0.0 to 1.0)
            status: Device status (e.g., 'active', 'inactive', 'maintenance')
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO device_metrics (device_id, utilization, status)
        VALUES (?, ?, ?)
        """, (device_id, utilization, status))
        conn.commit()
        conn.close()
    
    def record_link_metric(self, link_id: str, utilization: float, latency: float):
        """
        Record link performance metric
        
        Args:
            link_id: Unique identifier for the link
            utilization: Current link utilization percentage (0.0 to 1.0)
            latency: Current latency in milliseconds
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO link_metrics (link_id, utilization, latency)
        VALUES (?, ?, ?)
        """, (link_id, utilization, latency))
        conn.commit()
        conn.close()
    
    def record_service_log(self, service_id: str, event_type: str, details: str):
        """
        Record service event log
        
        Args:
            service_id: Unique identifier for the service
            event_type: Type of event (e.g., 'provisioned', 'decommissioned', 'failed')
            details: Additional details about the event
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO service_logs (service_id, event_type, details)
        VALUES (?, ?, ?)
        """, (service_id, event_type, details))
        conn.commit()
        conn.close()
    
    def get_device_metrics(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent metrics for a device
        
        Args:
            device_id: Unique identifier for the device
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of dictionaries containing timestamp, utilization, and status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT timestamp, utilization, status
        FROM device_metrics
        WHERE device_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (device_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "utilization": row[1],
                "status": row[2]
            })
        
        conn.close()
        return results
    
    def get_link_metrics(self, link_id: str, start_time: Optional[str] = None, 
                        end_time: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve link metrics with optional time range filtering
        
        Args:
            link_id: Unique identifier for the link
            start_time: Optional start timestamp for filtering (ISO format)
            end_time: Optional end timestamp for filtering (ISO format)
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of dictionaries containing timestamp, utilization, and latency
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT timestamp, utilization, latency
        FROM link_metrics
        WHERE link_id = ?
        """
        params = [link_id]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "utilization": row[1],
                "latency": row[2]
            })
        
        conn.close()
        return results
    
    def get_service_logs(self, service_id: str, event_type: Optional[str] = None, 
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve service logs with optional event type filtering
        
        Args:
            service_id: Unique identifier for the service
            event_type: Optional event type filter (e.g., 'provisioned', 'failed')
            limit: Maximum number of records to return (default: 100)
            
        Returns:
            List of dictionaries containing timestamp, event_type, and details
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT timestamp, event_type, details
        FROM service_logs
        WHERE service_id = ?
        """
        params = [service_id]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "timestamp": row[0],
                "event_type": row[1],
                "details": row[2]
            })
        
        conn.close()
        return results
    
    def close(self):
        """Close database connection (for cleanup)"""
        # SQLite connections are closed after each operation
        # This method is provided for API consistency
        pass

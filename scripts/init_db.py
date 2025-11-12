#!/usr/bin/env python3
"""
Database Initialization Script
Initializes Neo4j indexes and SQLite schema for IntelliNet Orchestrator
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from src.config import load_config


def init_neo4j(uri: str, user: str, password: str):
    """Initialize Neo4j database with indexes and constraints"""
    print("Initializing Neo4j database...")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            # Create indexes for Device nodes
            print("  Creating Device indexes...")
            session.run("CREATE INDEX device_id_index IF NOT EXISTS FOR (d:Device) ON (d.id)")
            session.run("CREATE INDEX device_type_index IF NOT EXISTS FOR (d:Device) ON (d.type)")
            
            # Create indexes for Service nodes
            print("  Creating Service indexes...")
            session.run("CREATE INDEX service_id_index IF NOT EXISTS FOR (s:Service) ON (s.id)")
            session.run("CREATE INDEX service_status_index IF NOT EXISTS FOR (s:Service) ON (s.status)")
            
            # Create indexes for User nodes
            print("  Creating User indexes...")
            session.run("CREATE INDEX user_username_index IF NOT EXISTS FOR (u:User) ON (u.username)")
            
            # Create uniqueness constraints
            print("  Creating uniqueness constraints...")
            try:
                session.run("CREATE CONSTRAINT device_id_unique IF NOT EXISTS FOR (d:Device) REQUIRE d.id IS UNIQUE")
                session.run("CREATE CONSTRAINT service_id_unique IF NOT EXISTS FOR (s:Service) REQUIRE s.id IS UNIQUE")
                session.run("CREATE CONSTRAINT user_username_unique IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE")
            except Exception as e:
                print(f"  Warning: Could not create constraints (may already exist): {e}")
            
            print("✓ Neo4j initialization completed successfully")
            
    except Exception as e:
        print(f"✗ Error initializing Neo4j: {e}")
        raise
    finally:
        driver.close()


def init_sqlite(db_path: str):
    """Initialize SQLite database with schema"""
    print(f"Initializing SQLite database at {db_path}...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create device_metrics table
        print("  Creating device_metrics table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            utilization REAL,
            status TEXT,
            capacity REAL,
            available_capacity REAL
        )
        """)
        
        # Create link_metrics table
        print("  Creating link_metrics table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS link_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            utilization REAL,
            latency REAL,
            bandwidth REAL,
            available_bandwidth REAL
        )
        """)
        
        # Create service_logs table
        print("  Creating service_logs table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            details TEXT,
            status TEXT
        )
        """)
        
        # Create indexes for better query performance
        print("  Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_metrics_device_id ON device_metrics(device_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_metrics_timestamp ON device_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_metrics_link_id ON link_metrics(link_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_link_metrics_timestamp ON link_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_logs_service_id ON service_logs(service_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_logs_timestamp ON service_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_service_logs_event_type ON service_logs(event_type)")
        
        conn.commit()
        print("✓ SQLite initialization completed successfully")
        
    except Exception as e:
        print(f"✗ Error initializing SQLite: {e}")
        raise
    finally:
        conn.close()


def main():
    """Main initialization function"""
    print("=" * 50)
    print("IntelliNet Orchestrator - Database Initialization")
    print("=" * 50)
    print()
    
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")
        print("Using environment variables...")
        config = None
    
    # Get database configuration from environment or config
    if config:
        neo4j_uri = config.get('database', {}).get('neo4j', {}).get('uri', 'bolt://localhost:7687')
        neo4j_user = config.get('database', {}).get('neo4j', {}).get('user', 'neo4j')
        neo4j_password = config.get('database', {}).get('neo4j', {}).get('password', 'password')
        sqlite_path = config.get('database', {}).get('metrics', {}).get('path', './data/metrics.db')
    else:
        neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
        neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
        sqlite_path = os.getenv('SQLITE_DB_PATH', './data/metrics.db')
    
    # Initialize databases
    try:
        init_neo4j(neo4j_uri, neo4j_user, neo4j_password)
        print()
        init_sqlite(sqlite_path)
        print()
        print("=" * 50)
        print("✓ All databases initialized successfully!")
        print("=" * 50)
        return 0
        
    except Exception as e:
        print()
        print("=" * 50)
        print(f"✗ Initialization failed: {e}")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
Development Backend Runner - Runs without Neo4j for testing
"""
import sys
import os

print("=" * 80)
print("IntelliNet Orchestrator - Development Mode")
print("=" * 80)
print()
print("⚠️  WARNING: This will attempt to start the backend.")
print("   Neo4j connection is required for full functionality.")
print()
print("Options:")
print("  1. Start Docker Desktop and run: docker-compose up -d")
print("  2. Install Neo4j locally and configure .env")
print("  3. Continue anyway (will fail on Neo4j connection)")
print()

choice = input("Continue? (y/n): ")

if choice.lower() != 'y':
    print("Exiting...")
    sys.exit(0)

print("\nStarting backend server...")
print("API will be available at: http://localhost:8000")
print("API Docs will be at: http://localhost:8000/api/docs")
print()

# Run the main application
os.system("python main.py")

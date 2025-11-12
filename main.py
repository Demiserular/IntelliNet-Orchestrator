"""
IntelliNet Orchestrator - Main Application Entry Point

This is the main entry point for the IntelliNet Orchestrator application.
It initializes and runs the FastAPI server with all configured components.
"""

import uvicorn
import sys
from pathlib import Path

from src.config import get_config
from src.logging_config import setup_logging, get_logger

# Initialize logging
setup_logging(log_level="INFO", log_file="intellinet_orchestrator.log", log_dir="logs")
logger = get_logger(__name__)


def main():
    """Main application entry point"""
    logger.info("=" * 80)
    logger.info("Starting IntelliNet Orchestrator")
    logger.info("=" * 80)
    
    # Load configuration
    config = get_config()
    
    # Log configuration
    logger.info(f"Environment: {config.environment}")
    logger.info(f"API Host: {config.api.host}")
    logger.info(f"API Port: {config.api.port}")
    logger.info(f"Neo4j URI: {config.neo4j.uri}")
    logger.info(f"Metrics DB: {config.metrics.path}")
    
    # Ensure data directory exists
    metrics_path = Path(config.metrics.path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run the application
    try:
        uvicorn.run(
            "src.api.app:app",
            host=config.api.host,
            port=config.api.port,
            reload=config.environment == "development",
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("IntelliNet Orchestrator stopped")


if __name__ == "__main__":
    main()

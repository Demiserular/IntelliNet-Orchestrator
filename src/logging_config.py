"""
Centralized logging configuration for IntelliNet Orchestrator.

This module provides consistent logging configuration across all components
of the application including API, services, repositories, and models.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "intellinet_orchestrator.log",
    log_dir: str = "logs"
) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name (None to disable file logging)
        log_dir: Directory for log files
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        full_log_path = log_path / log_file
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            full_log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_module_loggers(log_level)
    
    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    logger.info(f"Log level: {log_level}")
    if log_file:
        logger.info(f"Log file: {full_log_path}")


def configure_module_loggers(log_level: str = "INFO") -> None:
    """
    Configure logging levels for specific modules.
    
    Args:
        log_level: Default logging level
    """
    # Application modules
    logging.getLogger("src.api").setLevel(logging.INFO)
    logging.getLogger("src.services").setLevel(logging.INFO)
    logging.getLogger("src.repositories").setLevel(logging.INFO)
    logging.getLogger("src.models").setLevel(logging.INFO)
    
    # Third-party libraries (reduce noise)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Module-specific logger helpers
def log_api_request(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float) -> None:
    """Log API request details."""
    logger.info(f"{method} {path} - {status_code} - {duration_ms:.2f}ms")


def log_service_operation(logger: logging.Logger, operation: str, service_id: str, success: bool, message: str = "") -> None:
    """Log service orchestration operations."""
    level = logging.INFO if success else logging.ERROR
    status = "SUCCESS" if success else "FAILED"
    logger.log(level, f"Service {operation} - {service_id} - {status} - {message}")


def log_repository_operation(logger: logging.Logger, operation: str, entity_type: str, entity_id: str, success: bool) -> None:
    """Log repository operations."""
    level = logging.DEBUG if success else logging.ERROR
    status = "SUCCESS" if success else "FAILED"
    logger.log(level, f"Repository {operation} - {entity_type}:{entity_id} - {status}")


def log_rule_evaluation(logger: logging.Logger, rule_id: str, service_id: str, passed: bool, message: str = "") -> None:
    """Log rule engine evaluations."""
    level = logging.INFO if passed else logging.WARNING
    status = "PASSED" if passed else "FAILED"
    logger.log(level, f"Rule {rule_id} - Service {service_id} - {status} - {message}")

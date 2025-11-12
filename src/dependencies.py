"""
Dependency Injection Container for IntelliNet Orchestrator.

This module provides a centralized dependency injection system for managing
application components and their lifecycle.
"""

from typing import Optional
from contextlib import contextmanager
import logging

from src.config import get_config
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.repositories.user_repository import UserRepository
from src.services.rule_engine import RuleEngine
from src.services.service_orchestrator import ServiceOrchestrator
from src.services.auth_service import AuthService
from src.logging_config import get_logger

logger = get_logger(__name__)


class DependencyContainer:
    """
    Dependency injection container for managing application components.
    
    This class follows the singleton pattern and provides centralized
    access to all application services and repositories.
    """
    
    _instance: Optional['DependencyContainer'] = None
    
    def __init__(self):
        """Initialize the dependency container."""
        self._neo4j_repo: Optional[Neo4jRepository] = None
        self._metrics_repo: Optional[MetricsRepository] = None
        self._user_repo: Optional[UserRepository] = None
        self._rule_engine: Optional[RuleEngine] = None
        self._service_orchestrator: Optional[ServiceOrchestrator] = None
        self._auth_service: Optional[AuthService] = None
        self._initialized = False
    
    @classmethod
    def get_instance(cls) -> 'DependencyContainer':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, config_file: str = "config.yaml") -> None:
        """
        Initialize all dependencies.
        
        Args:
            config_file: Path to configuration file
        """
        if self._initialized:
            logger.warning("Dependency container already initialized")
            return
        
        logger.info("Initializing dependency container...")
        
        # Load configuration
        config = get_config(config_file)
        
        # Initialize repositories
        logger.info("Initializing repositories...")
        self._neo4j_repo = Neo4jRepository(
            uri=config.neo4j.uri,
            user=config.neo4j.user,
            password=config.neo4j.password
        )
        logger.info(f"Neo4j repository initialized: {config.neo4j.uri}")
        
        self._metrics_repo = MetricsRepository(db_path=config.metrics.path)
        logger.info(f"Metrics repository initialized: {config.metrics.path}")
        
        self._user_repo = UserRepository(db_path=config.metrics.path)
        logger.info("User repository initialized")
        
        # Initialize services
        logger.info("Initializing services...")
        self._rule_engine = RuleEngine()
        logger.info("Rule engine initialized")
        
        self._service_orchestrator = ServiceOrchestrator(
            neo4j_repo=self._neo4j_repo,
            metrics_repo=self._metrics_repo,
            rule_engine=self._rule_engine
        )
        logger.info("Service orchestrator initialized")
        
        self._auth_service = AuthService(
            user_repository=self._user_repo,
            secret_key=config.security.jwt_secret,
            token_expire_minutes=config.security.token_expiry
        )
        logger.info("Auth service initialized")
        
        self._initialized = True
        logger.info("Dependency container initialization complete")
    
    def shutdown(self) -> None:
        """Shutdown and cleanup all dependencies."""
        if not self._initialized:
            logger.warning("Dependency container not initialized")
            return
        
        logger.info("Shutting down dependency container...")
        
        # Close repositories
        if self._neo4j_repo:
            self._neo4j_repo.close()
            logger.info("Neo4j repository closed")
        
        if self._metrics_repo:
            self._metrics_repo.close()
            logger.info("Metrics repository closed")
        
        if self._user_repo:
            self._user_repo.close()
            logger.info("User repository closed")
        
        # Reset state
        self._neo4j_repo = None
        self._metrics_repo = None
        self._user_repo = None
        self._rule_engine = None
        self._service_orchestrator = None
        self._auth_service = None
        self._initialized = False
        
        logger.info("Dependency container shutdown complete")
    
    @property
    def neo4j_repository(self) -> Neo4jRepository:
        """Get Neo4j repository instance."""
        if not self._initialized or self._neo4j_repo is None:
            raise RuntimeError("Neo4j repository not initialized")
        return self._neo4j_repo
    
    @property
    def metrics_repository(self) -> MetricsRepository:
        """Get metrics repository instance."""
        if not self._initialized or self._metrics_repo is None:
            raise RuntimeError("Metrics repository not initialized")
        return self._metrics_repo
    
    @property
    def user_repository(self) -> UserRepository:
        """Get user repository instance."""
        if not self._initialized or self._user_repo is None:
            raise RuntimeError("User repository not initialized")
        return self._user_repo
    
    @property
    def rule_engine(self) -> RuleEngine:
        """Get rule engine instance."""
        if not self._initialized or self._rule_engine is None:
            raise RuntimeError("Rule engine not initialized")
        return self._rule_engine
    
    @property
    def service_orchestrator(self) -> ServiceOrchestrator:
        """Get service orchestrator instance."""
        if not self._initialized or self._service_orchestrator is None:
            raise RuntimeError("Service orchestrator not initialized")
        return self._service_orchestrator
    
    @property
    def auth_service(self) -> AuthService:
        """Get auth service instance."""
        if not self._initialized or self._auth_service is None:
            raise RuntimeError("Auth service not initialized")
        return self._auth_service
    
    @property
    def is_initialized(self) -> bool:
        """Check if container is initialized."""
        return self._initialized


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    global _container
    if _container is None:
        _container = DependencyContainer.get_instance()
    return _container


@contextmanager
def container_context(config_file: str = "config.yaml"):
    """
    Context manager for dependency container lifecycle.
    
    Usage:
        with container_context() as container:
            # Use container
            repo = container.neo4j_repository
    """
    container = get_container()
    try:
        container.initialize(config_file)
        yield container
    finally:
        container.shutdown()


# Convenience functions for FastAPI dependency injection
def get_neo4j_repository() -> Neo4jRepository:
    """FastAPI dependency for Neo4j repository."""
    return get_container().neo4j_repository


def get_metrics_repository() -> MetricsRepository:
    """FastAPI dependency for metrics repository."""
    return get_container().metrics_repository


def get_user_repository() -> UserRepository:
    """FastAPI dependency for user repository."""
    return get_container().user_repository


def get_rule_engine() -> RuleEngine:
    """FastAPI dependency for rule engine."""
    return get_container().rule_engine


def get_service_orchestrator() -> ServiceOrchestrator:
    """FastAPI dependency for service orchestrator."""
    return get_container().service_orchestrator


def get_auth_service() -> AuthService:
    """FastAPI dependency for auth service."""
    return get_container().auth_service

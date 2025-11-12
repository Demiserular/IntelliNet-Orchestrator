"""Configuration management module for environment-based settings."""

import os
import yaml
from typing import Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Neo4jConfig(BaseSettings):
    """Neo4j database configuration."""
    uri: str = Field(default="bolt://localhost:7687")
    user: str = Field(default="neo4j")
    password: str = Field(default="")

    class Config:
        env_prefix = "NEO4J_"


class MetricsConfig(BaseSettings):
    """Metrics database configuration."""
    type: str = Field(default="sqlite")
    path: str = Field(default="./data/metrics.db")

    class Config:
        env_prefix = "METRICS_"


class APIConfig(BaseSettings):
    """API server configuration."""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_origins: Union[list[str], str] = Field(default_factory=lambda: ["http://localhost:4200"])

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_prefix = "API_"


class SecurityConfig(BaseSettings):
    """Security configuration."""
    jwt_secret: str = Field(default="")
    token_expiry: int = Field(default=3600)

    class Config:
        env_prefix = "SECURITY_"


class RulesConfig(BaseSettings):
    """Rule engine configuration."""
    config_path: str = Field(default="./config/rules.json")
    auto_reload: bool = Field(default=True)

    class Config:
        env_prefix = "RULES_"


class AppConfig:
    """Main application configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Load from YAML if provided
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                yaml_config = yaml.safe_load(f)
                self._load_from_yaml(yaml_config)
        
        # Initialize sub-configs (environment variables take precedence)
        self.neo4j = Neo4jConfig()
        self.metrics = MetricsConfig()
        self.api = APIConfig()
        self.security = SecurityConfig()
        self.rules = RulesConfig()
    
    def _load_from_yaml(self, yaml_config: dict):
        """Load configuration from YAML file."""
        if 'environment' in yaml_config:
            self.environment = yaml_config['environment']
        
        # Set environment variables from YAML (if not already set)
        if 'database' in yaml_config:
            db_config = yaml_config['database']
            if 'neo4j' in db_config:
                for key, value in db_config['neo4j'].items():
                    env_key = f"NEO4J_{key.upper()}"
                    if env_key not in os.environ:
                        os.environ[env_key] = str(value)
            
            if 'metrics' in db_config:
                for key, value in db_config['metrics'].items():
                    env_key = f"METRICS_{key.upper()}"
                    if env_key not in os.environ:
                        os.environ[env_key] = str(value)
        
        if 'api' in yaml_config:
            for key, value in yaml_config['api'].items():
                env_key = f"API_{key.upper()}"
                if env_key not in os.environ:
                    if isinstance(value, list):
                        os.environ[env_key] = ','.join(value)
                    else:
                        os.environ[env_key] = str(value)
        
        if 'security' in yaml_config:
            for key, value in yaml_config['security'].items():
                env_key = f"SECURITY_{key.upper()}"
                if env_key not in os.environ:
                    os.environ[env_key] = str(value)
        
        if 'rules' in yaml_config:
            for key, value in yaml_config['rules'].items():
                env_key = f"RULES_{key.upper()}"
                if env_key not in os.environ:
                    os.environ[env_key] = str(value)


# Global config instance
config: Optional[AppConfig] = None


def get_config(config_file: str = "config.yaml") -> AppConfig:
    """Get or create the global configuration instance."""
    global config
    if config is None:
        config = AppConfig(config_file)
    return config

"""Master configuration class"""
from app.config.secrets import Config as SecretsConfig
from app.config.database import Config as DatabaseConfig
from app.config.dev import Config as DevConfig

class Config(DevConfig, DatabaseConfig, SecretsConfig):
    """Builds configuration for development"""

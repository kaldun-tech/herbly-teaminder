"""Master configuration class"""
from dev import Config as DevConfig
from database import Config as DatabaseConfig
from prod import Config as ProdConfig
from secrets import Config as SecretsConfig

class Config(DevConfig, DatabaseConfig, SecretsConfig):
    """Builds configuration for development"""
    pass

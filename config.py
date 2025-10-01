"""
Configuration management for JobMiner.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ScraperConfig:
    """Configuration for individual scrapers."""
    delay: float = 2.0
    timeout: int = 30
    max_retries: int = 3
    user_agent: Optional[str] = None
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class DatabaseConfig:
    """Database configuration."""
    enabled: bool = False
    url: str = "sqlite:///jobminer.db"
    echo: bool = False


@dataclass
class JobMinerConfig:
    """Main JobMiner configuration."""
    # Output settings
    default_output_format: str = "both"  # json, csv, both
    output_directory: str = "output"
    
    # Scraper settings
    default_scraper_config: ScraperConfig = None
    
    # Database settings
    database: DatabaseConfig = None
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    def __post_init__(self):
        if self.default_scraper_config is None:
            self.default_scraper_config = ScraperConfig()
        if self.database is None:
            self.database = DatabaseConfig()


class ConfigManager:
    """Manages JobMiner configuration."""
    
    def __init__(self, config_file: str = "jobminer_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> JobMinerConfig:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return self._dict_to_config(data)
            except Exception as e:
                print(f"Warning: Error loading config file: {e}")
                print("Using default configuration.")
        
        return JobMinerConfig()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config_to_dict(self.config), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _config_to_dict(self, config: JobMinerConfig) -> Dict[str, Any]:
        """Convert config object to dictionary."""
        return {
            'default_output_format': config.default_output_format,
            'output_directory': config.output_directory,
            'default_scraper_config': asdict(config.default_scraper_config),
            'database': asdict(config.database),
            'log_level': config.log_level,
            'log_file': config.log_file
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> JobMinerConfig:
        """Convert dictionary to config object."""
        scraper_config_data = data.get('default_scraper_config', {})
        scraper_config = ScraperConfig(**scraper_config_data)
        
        database_config_data = data.get('database', {})
        database_config = DatabaseConfig(**database_config_data)
        
        return JobMinerConfig(
            default_output_format=data.get('default_output_format', 'both'),
            output_directory=data.get('output_directory', 'output'),
            default_scraper_config=scraper_config,
            database=database_config,
            log_level=data.get('log_level', 'INFO'),
            log_file=data.get('log_file')
        )
    
    def get_scraper_config(self, scraper_name: str) -> ScraperConfig:
        """Get configuration for a specific scraper."""
        # For now, return default config
        # In the future, could support per-scraper configs
        return self.config.default_scraper_config
    
    def update_scraper_config(self, **kwargs):
        """Update default scraper configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.default_scraper_config, key):
                setattr(self.config.default_scraper_config, key, value)
        self.save_config()
    
    def update_database_config(self, **kwargs):
        """Update database configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config.database, key):
                setattr(self.config.database, key, value)
        self.save_config()


# Environment variable helpers
def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable with optional default."""
    return os.getenv(key, default)


def get_database_url() -> str:
    """Get database URL from environment or config."""
    return get_env_var('JOBMINER_DATABASE_URL', 'sqlite:///jobminer.db')


def get_log_level() -> str:
    """Get log level from environment or config."""
    return get_env_var('JOBMINER_LOG_LEVEL', 'INFO')


# Global config instance
config_manager = ConfigManager()


def get_config() -> JobMinerConfig:
    """Get the global configuration."""
    return config_manager.config


def save_config():
    """Save the global configuration."""
    config_manager.save_config()


# Example configuration file content
EXAMPLE_CONFIG = {
    "default_output_format": "both",
    "output_directory": "output",
    "default_scraper_config": {
        "delay": 2.0,
        "timeout": 30,
        "max_retries": 3,
        "user_agent": null,
        "headers": {}
    },
    "database": {
        "enabled": False,
        "url": "sqlite:///jobminer.db",
        "echo": False
    },
    "log_level": "INFO",
    "log_file": null
}

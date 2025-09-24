
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 1236
    user: str = "postgres"
    password: str = "password"
    name: str = "chatbot_db"
    
    @property
    def url(self) -> str:
        """Get database connection URL"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class LLMConfig:
    """LLM provider configuration settings"""
    provider: str = "groq"  # groq or openai
    temperature: float = 0.7
    
    # Groq settings
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    
    def get_api_key(self) -> str:
        """Get the appropriate API key based on provider"""
        if self.provider == "groq":
            return self.groq_api_key
        elif self.provider == "openai":
            return self.openai_api_key
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def get_model(self) -> str:
        """Get the appropriate model based on provider"""
        if self.provider == "groq":
            return self.groq_model
        elif self.provider == "openai":
            return self.openai_model
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")


@dataclass
class ServerConfig:
    """Server configuration settings"""
    host: str = "0.0.0.0"
    port: int = 1234
    backend_internal_port: int = 8000
    ui_port: int = 1235
    ui_internal_port: int = 80
    environment: str = "development"
    log_level: str = "info"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    @property
    def reload(self) -> bool:
        """Whether to enable auto-reload (only in development)"""
        return self.is_development


@dataclass
class NetworkConfig:
    """Network configuration settings"""
    name: str = "chatbot_net"
    health_check_interval: str = "30s"
    health_check_timeout: str = "10s"
    health_check_retries: int = 3
    backend_start_period: str = "40s"
    ui_start_period: str = "20s"
    db_start_period: str = "30s"


class Configures:
    """Main configuration class for the chatbot application."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration from environment variables
        
        Args:
            env_file: Optional path to .env file (defaults to .env in current directory)
        """
        # Load environment variables
        load_dotenv(env_file)
        
        # Initialize configuration sections
        self.database = self._load_database_config()
        self.llm = self._load_llm_config()
        self.server = self._load_server_config()
        self.network = self._load_network_config()
        
        # Validate configuration
        self.validate()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment variables"""
        return DatabaseConfig(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_INTERNAL_PORT", "1236")),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            name=os.getenv("POSTGRES_DB", "chatbot_db")
        )
    
    def _load_llm_config(self) -> LLMConfig:
        """Load LLM configuration from environment variables"""
        return LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "groq").lower(),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("LLM_MODEL", "gpt-4o")
        )
    
    def _load_server_config(self) -> ServerConfig:
        """Load server configuration from environment variables"""
        return ServerConfig(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("CHATBOT_BACKEND_PORT", "1234")),
            backend_internal_port=int(os.getenv("BACKEND_INTERNAL_PORT", "8000")),
            ui_port=int(os.getenv("CHATBOT_UI_PORT", "1235")),
            ui_internal_port=int(os.getenv("UI_INTERNAL_PORT", "80")),
            environment=os.getenv("ENVIRONMENT", "development"),
            log_level=os.getenv("LOG_LEVEL", "info").lower()
        )
    
    def _load_network_config(self) -> NetworkConfig:
        """Load network configuration from environment variables"""
        return NetworkConfig(
            name=os.getenv("NETWORK_NAME", "chatbot_net"),
            health_check_interval=os.getenv("HEALTH_CHECK_INTERVAL", "30s"),
            health_check_timeout=os.getenv("HEALTH_CHECK_TIMEOUT", "10s"),
            health_check_retries=int(os.getenv("HEALTH_CHECK_RETRIES", "3")),
            backend_start_period=os.getenv("BACKEND_START_PERIOD", "40s"),
            ui_start_period=os.getenv("UI_START_PERIOD", "20s"),
            db_start_period=os.getenv("DB_START_PERIOD", "30s")
        )
    
    def validate(self) -> None:
        """
        Validate configuration settings
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        errors = []
        
        # Validate LLM configuration
        if not self.llm.provider:
            errors.append("LLM provider must be specified")
        elif self.llm.provider not in ["groq", "openai"]:
            errors.append(f"Unsupported LLM provider: {self.llm.provider}")
        
        # Validate API keys based on provider
        try:
            api_key = self.llm.get_api_key()
            if not api_key:
                errors.append(f"API key required for {self.llm.provider} provider")
        except ValueError as e:
            errors.append(str(e))
        
        # Validate temperature range
        if not 0.0 <= self.llm.temperature <= 2.0:
            errors.append(f"Temperature must be between 0.0 and 2.0, got: {self.llm.temperature}")
        
        # Validate database configuration
        if not self.database.host:
            errors.append("Database host must be specified")
        if not self.database.user:
            errors.append("Database user must be specified")
        if not self.database.name:
            errors.append("Database name must be specified")
        if not 1 <= self.database.port <= 65535:
            errors.append(f"Database port must be between 1 and 65535, got: {self.database.port}")
        
        # Validate server configuration
        if not 1 <= self.server.port <= 65535:
            errors.append(f"Server port must be between 1 and 65535, got: {self.server.port}")
        if not 1 <= self.server.ui_port <= 65535:
            errors.append(f"UI port must be between 1 and 65535, got: {self.server.ui_port}")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    def get_safe_config(self) -> Dict[str, Any]:
        """
        Get configuration dictionary with sensitive information redacted
        
        Returns:
            Dictionary containing configuration with API keys and passwords masked
        """
        safe_config = {
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "user": self.database.user,
                "password": "***" if self.database.password else None,
                "name": self.database.name
            },
            "llm": {
                "provider": self.llm.provider,
                "temperature": self.llm.temperature,
                "model": self.llm.get_model(),
                "api_key": "***" if self.llm.get_api_key() else None
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "backend_internal_port": self.server.backend_internal_port,
                "ui_port": self.server.ui_port,
                "ui_internal_port": self.server.ui_internal_port,
                "environment": self.server.environment,
                "log_level": self.server.log_level,
                "is_development": self.server.is_development
            },
            "network": {
                "name": self.network.name,
                "health_check_interval": self.network.health_check_interval,
                "health_check_timeout": self.network.health_check_timeout,
                "health_check_retries": self.network.health_check_retries
            }
        }
        return safe_config
    
    def log_config(self) -> str:
        """
        Get a formatted string representation of the configuration for logging
        
        Returns:
            Formatted string with configuration details (sensitive data redacted)
        """
        config = self.get_safe_config()
        lines = [
            "📋 Configuration Settings:",
            f"  🗄️  Database: {config['database']['user']}@{config['database']['host']}:{config['database']['port']}/{config['database']['name']}",
            f"  🤖 LLM: {config['llm']['provider']} ({config['llm']['model']}) - Temperature: {config['llm']['temperature']}",
            f"  🌐 Server: {config['server']['host']}:{config['server']['port']} ({config['server']['environment']})",
            f"  🔗 Network: {config['network']['name']}",
            f"  📊 Log Level: {config['server']['log_level']}"
        ]
        return "\n".join(lines)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Configures':
        """
        Create configuration instance from dictionary
        
        Args:
            config_dict: Dictionary containing configuration values
            
        Returns:
            Configures instance
        """
        # Set environment variables from dictionary
        for key, value in config_dict.items():
            os.environ[key.upper()] = str(value)
        
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Returns:
            Dictionary containing all configuration values
        """
        return {
            # Database settings
            "POSTGRES_HOST": self.database.host,
            "POSTGRES_INTERNAL_PORT": str(self.database.port),
            "POSTGRES_USER": self.database.user,
            "POSTGRES_PASSWORD": self.database.password,
            "POSTGRES_DB": self.database.name,
            
            # LLM settings
            "LLM_PROVIDER": self.llm.provider,
            "TEMPERATURE": str(self.llm.temperature),
            "GROQ_API_KEY": self.llm.groq_api_key,
            "GROQ_MODEL": self.llm.groq_model,
            "OPENAI_API_KEY": self.llm.openai_api_key,
            "LLM_MODEL": self.llm.openai_model,
            
            # Server settings
            "HOST": self.server.host,
            "CHATBOT_BACKEND_PORT": str(self.server.port),
            "BACKEND_INTERNAL_PORT": str(self.server.backend_internal_port),
            "CHATBOT_UI_PORT": str(self.server.ui_port),
            "UI_INTERNAL_PORT": str(self.server.ui_internal_port),
            "ENVIRONMENT": self.server.environment,
            "LOG_LEVEL": self.server.log_level,
            
            # Network settings
            "NETWORK_NAME": self.network.name,
            "HEALTH_CHECK_INTERVAL": self.network.health_check_interval,
            "HEALTH_CHECK_TIMEOUT": self.network.health_check_timeout,
            "HEALTH_CHECK_RETRIES": str(self.network.health_check_retries),
            "BACKEND_START_PERIOD": self.network.backend_start_period,
            "UI_START_PERIOD": self.network.ui_start_period,
            "DB_START_PERIOD": self.network.db_start_period
        }


# Global configuration instance
config = Configures()
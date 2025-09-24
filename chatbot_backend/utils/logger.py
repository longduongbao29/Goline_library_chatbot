import logging
import os
from datetime import datetime
from pathlib import Path

class Logger:
    """Simple logger class for easy logging configuration"""
    
    def __init__(self, name: str = "chatbot", log_dir: str = "logs", log_file: str = "backend.logs"):
        """
        Initialize logger
        
        Args:
            name: Logger name (default: "chatbot")
            log_dir: Directory to store log files (default: "logs")
            log_file: Custom log file name (default: auto-generated)
        """
        self.logger = logging.getLogger(name)
        self.log_dir = log_dir
        
        # Create logs directory if not exists
        Path(log_dir).mkdir(exist_ok=True)
        
        # Generate log file name if not provided
        if not log_file:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = f"{name}_{timestamp}.log"
        
        self.log_file = os.path.join(log_dir, log_file)
        
        # Setup logger
        self._setup_logger()
    def get_logger(self):
        return self.logger
    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Get environment setting - try config first, fallback to os.getenv
        try:
            from config.configures import config
            environment = config.server.environment
            log_level = config.server.log_level
        except (ImportError, AttributeError):
            # Fallback for cases where config isn't available yet
            environment = os.getenv('ENVIRONMENT', 'development').lower()
            log_level = os.getenv('LOG_LEVEL', 'info').lower()
        
        # Set logging levels based on environment and log_level config
        level_mapping = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        # Use configured log level if available, otherwise default by environment
        if 'log_level' in locals() and log_level in level_mapping:
            logger_level = console_level = file_level = level_mapping[log_level]
        elif environment == 'production':
            logger_level = console_level = file_level = logging.INFO
        else:  # development or any other environment
            logger_level = console_level = file_level = logging.DEBUG
        
        # Set logger level
        self.logger.setLevel(logger_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log environment info
        if environment == 'production':
            self.logger.info(f"Logger initialized in PRODUCTION mode - Level: INFO")
        else:
            self.logger.debug(f"Logger initialized in DEVELOPMENT mode - Level: DEBUG")
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def set_file_level(self, level: str):
        """
        Set log level for file output
        
        Args:
            level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.setLevel(level_map[level.upper()])
    
    def set_console_level(self, level: str):
        """
        Set log level for console output
        
        Args:
            level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(level_map[level.upper()])

# Global logger instance
_global_logger = None

def get_logger(name: str = "chatbot", log_dir: str = "logs") -> Logger:
    """
    Get or create a global logger instance
    
    Args:
        name: Logger name
        log_dir: Log directory
        
    Returns:
        Logger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = Logger(name=name, log_dir=log_dir)
    
    return _global_logger

# Convenience functions for quick logging
def debug(message: str):
    """Quick debug log"""
    get_logger().debug(message)

def info(message: str):
    """Quick info log"""
    get_logger().info(message)

def warning(message: str):
    """Quick warning log"""
    get_logger().warning(message)

def error(message: str):
    """Quick error log"""
    get_logger().error(message)

def critical(message: str):
    """Quick critical log"""
    get_logger().critical(message)

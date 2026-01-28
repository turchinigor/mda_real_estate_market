"""
Logging configuration module for the project.
Centralizes logging setup for all scripts.
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logging(
    name: str = "mda_real_estate",
    log_dir: str | Path = None,
    level: int = logging.INFO,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Configure and return a logger instance with both file and console handlers.
    
    Args:
        name: Logger name (default: "mda_real_estate")
        log_dir: Directory to store log files (default: project_root/logs)
        level: Overall logger level (default: INFO)
        console_level: Console handler level (default: INFO)
        file_level: File handler level (default: DEBUG)
    
    Returns:
        Configured logger instance
    """
    # Set up log directory
    if log_dir is None:
        # Find project root (parent of src directory)
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
    else:
        log_dir = Path(log_dir)
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # Define log format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # File Handler (all levels - DEBUG and above)
    # Rotating file handler - creates new file when size reaches 5MB
    log_file = log_dir / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Separate handler for errors (ERROR and above)
    error_log_file = log_dir / f"{name}_errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str = "mda_real_estate") -> logging.Logger:
    """
    Get an already configured logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

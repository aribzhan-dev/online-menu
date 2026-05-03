import logging
import sys
from pathlib import Path

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create formatters
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(LOG_DIR / "app.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Error file handler
error_handler = logging.FileHandler(LOG_DIR / "error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Root logger configuration
def setup_logging():
    """Setup application logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for module"""
    return logging.getLogger(name)

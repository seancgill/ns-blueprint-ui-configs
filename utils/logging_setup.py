import logging
import os
from logging.handlers import RotatingFileHandler

# Default configuration values
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
DEFAULT_LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "netsapiens_api.log")
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Flag to prevent multiple configurations
_logging_configured = False
_logger = None

def setup_logging(log_level=None, log_dir=None, log_file=None, log_format=None):
    global _logging_configured, _logger
    if _logging_configured:
        return _logger

    # Use defaults if not provided
    log_level = log_level or DEFAULT_LOG_LEVEL
    log_dir = log_dir or DEFAULT_LOG_DIR
    log_file = log_file or DEFAULT_LOG_FILE
    log_format = log_format or DEFAULT_LOG_FORMAT

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create a named logger
    logger = logging.getLogger("netsapiens_api")
    logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # Create handlers
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5  # Keep up to 5 backup files
    )
    stream_handler = logging.StreamHandler()

    # Create formatter
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    _logging_configured = True
    _logger = logger
    return _logger

# Configure logging on import with defaults
setup_logging()
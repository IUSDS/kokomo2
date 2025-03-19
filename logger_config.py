import logging
import logging.config
#import os

# Define log file paths
APP_LOG_FILE = "logs/app.log"
UVICORN_ACCESS_LOG_FILE = "logs/uvicorn_access.log"
UVICORN_ERROR_LOG_FILE = "logs/uvicorn_error.log"
WEBHOOK_LOG_FILE = "logs/webhooks.log"

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "uvicorn": {
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "app_handler": {
            "class": "logging.FileHandler",
            "filename": APP_LOG_FILE,
            "formatter": "detailed",
            "level": "INFO",
        },
        "uvicorn_access_handler": {
            "class": "logging.FileHandler",
            "filename": UVICORN_ACCESS_LOG_FILE,
            "formatter": "uvicorn",
            "level": "INFO",
        },
        "uvicorn_error_handler": {
            "class": "logging.FileHandler",
            "filename": UVICORN_ERROR_LOG_FILE,
            "formatter": "uvicorn",
            "level": "ERROR",
        },
    },
    "loggers": {
        "app_logger": {
            "handlers": ["app_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["uvicorn_access_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["uvicorn_error_handler"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Apply logging configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Get loggers
app_logger = logging.getLogger("app_logger")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_error_logger = logging.getLogger("uvicorn.error")

# Configure logging
logging.basicConfig(
    filename=WEBHOOK_LOG_FILE,
    filemode="a",  # Append to the log file
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Create a logger instance
logger = logging.getLogger("webhook_logger")

"""Logger configuration for Supply Chain Optimizer."""

import json
import logging
import logging.handlers
import os
from pathlib import Path

from .environment import config

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "supply-chain-optimizer",
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


def setup_logger(name: str = "supply-chain-optimizer") -> logging.Logger:
    """Set up and configure logger."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.logging.level))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.logging.level))

    if config.logging.format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for errors
    error_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "error.log", maxBytes=10485760, backupCount=5
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)

    # File handler for all logs
    combined_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "combined.log", maxBytes=10485760, backupCount=5
    )
    combined_file_handler.setLevel(getattr(logging, config.logging.level))
    combined_file_handler.setFormatter(formatter)
    logger.addHandler(combined_file_handler)

    return logger


logger = setup_logger()

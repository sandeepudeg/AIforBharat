"""Supply Chain Optimizer - Multi-agent AI system for supply chain optimization."""

__version__ = "1.0.0"
__author__ = "Supply Chain Team"

from src.config import config, logger
from src.observability import setup_xray_tracing

__all__ = ["config", "logger", "setup_xray_tracing"]

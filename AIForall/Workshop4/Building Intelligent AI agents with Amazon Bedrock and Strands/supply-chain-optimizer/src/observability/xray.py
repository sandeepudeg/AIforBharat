"""X-Ray tracing setup for Supply Chain Optimizer."""

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

from src.config import config, logger


def setup_xray_tracing() -> None:
    """Set up AWS X-Ray tracing for distributed tracing."""
    try:
        if config.app.is_production:
            xray_recorder.configure(
                service="supply-chain-optimizer",
                context_missing="LOG_ERROR",
            )
            patch_all()
            logger.info("X-Ray tracing configured successfully")
        else:
            logger.info("X-Ray tracing disabled in development mode")
    except Exception as e:
        logger.error(f"Failed to configure X-Ray tracing: {str(e)}")
        # Don't raise - allow application to continue without tracing

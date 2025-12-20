"""Main entry point for Supply Chain Optimizer."""

import sys
from typing import Optional, Dict, Any

from src.config import config, logger
from src.observability import setup_xray_tracing
from src.aws import (
    get_dynamodb_client,
    get_dynamodb_resource,
    get_eventbridge_client,
    get_lambda_client,
    get_rds_client,
    get_s3_client,
    get_sns_client,
)
from src.orchestration.setup import EventDrivenSetup


def initialize_application(setup_orchestration: bool = False) -> Dict[str, Any]:
    """Initialize the Supply Chain Optimizer application.
    
    Args:
        setup_orchestration: Whether to set up EventBridge rules and Lambda targets
    
    Returns:
        Dictionary with initialized AWS service clients
    """
    try:
        logger.info("Initializing Supply Chain Optimizer...")
        logger.info(f"Environment: {config.app.node_env}")
        logger.info(f"AWS Region: {config.aws.region}")

        # Set up X-Ray tracing
        setup_xray_tracing()

        # Initialize AWS service clients
        logger.info("Initializing AWS service clients...")
        rds_client = get_rds_client()
        dynamodb_client = get_dynamodb_client()
        dynamodb_resource = get_dynamodb_resource()
        s3_client = get_s3_client()
        lambda_client = get_lambda_client()
        eventbridge_client = get_eventbridge_client()
        sns_client = get_sns_client()

        logger.info("All AWS service clients initialized successfully")

        # Set up event-driven orchestration if requested
        if setup_orchestration:
            logger.info("Setting up event-driven orchestration...")
            setup = EventDrivenSetup()
            result = setup.setup_all_rules()
            if result["status"] == "success":
                logger.info("Event-driven orchestration setup completed successfully")
            else:
                logger.warning(f"Event-driven orchestration setup completed with issues: {result['errors']}")

        logger.info("Supply Chain Optimizer initialized successfully")

        return {
            "rds": rds_client,
            "dynamodb_client": dynamodb_client,
            "dynamodb_resource": dynamodb_resource,
            "s3": s3_client,
            "lambda": lambda_client,
            "eventbridge": eventbridge_client,
            "sns": sns_client,
        }

    except Exception as e:
        logger.error(f"Failed to initialize Supply Chain Optimizer: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main function."""
    logger.info("Starting Supply Chain Optimizer...")
    clients = initialize_application(setup_orchestration=False)
    logger.info("Application ready for agent execution")


if __name__ == "__main__":
    main()

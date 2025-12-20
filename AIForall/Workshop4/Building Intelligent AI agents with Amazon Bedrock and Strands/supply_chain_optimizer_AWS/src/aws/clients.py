"""AWS service clients for Supply Chain Optimizer."""

from typing import Any, Optional

import boto3
from botocore.config import Config

from src.config import config, logger


def _get_boto3_config() -> Config:
    """Get boto3 configuration."""
    return Config(
        region_name=config.aws.region,
        retries={"max_attempts": 3, "mode": "adaptive"},
        connect_timeout=5,
        read_timeout=60,
    )


def get_rds_client() -> Any:
    """Get RDS client."""
    try:
        client = boto3.client(
            "rds",
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            config=_get_boto3_config(),
        )
        logger.info("RDS client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize RDS client: {str(e)}")
        raise


def get_dynamodb_client() -> Any:
    """Get DynamoDB client."""
    try:
        kwargs = {
            "region_name": config.dynamodb.region,
            "aws_access_key_id": config.aws.access_key_id,
            "aws_secret_access_key": config.aws.secret_access_key,
            "config": _get_boto3_config(),
        }

        if config.dynamodb.endpoint:
            kwargs["endpoint_url"] = config.dynamodb.endpoint

        client = boto3.client("dynamodb", **kwargs)
        logger.info("DynamoDB client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
        raise


def get_dynamodb_resource() -> Any:
    """Get DynamoDB resource."""
    try:
        kwargs = {
            "region_name": config.dynamodb.region,
            "aws_access_key_id": config.aws.access_key_id,
            "aws_secret_access_key": config.aws.secret_access_key,
        }

        if config.dynamodb.endpoint:
            kwargs["endpoint_url"] = config.dynamodb.endpoint

        resource = boto3.resource("dynamodb", **kwargs)
        logger.info("DynamoDB resource initialized successfully")
        return resource
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB resource: {str(e)}")
        raise


def get_s3_client() -> Any:
    """Get S3 client."""
    try:
        client = boto3.client(
            "s3",
            region_name=config.s3.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            config=_get_boto3_config(),
        )
        logger.info("S3 client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {str(e)}")
        raise


def get_lambda_client() -> Any:
    """Get Lambda client."""
    try:
        client = boto3.client(
            "lambda",
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            config=_get_boto3_config(),
        )
        logger.info("Lambda client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Lambda client: {str(e)}")
        raise


def get_eventbridge_client() -> Any:
    """Get EventBridge client."""
    try:
        client = boto3.client(
            "events",
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            config=_get_boto3_config(),
        )
        logger.info("EventBridge client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize EventBridge client: {str(e)}")
        raise


def get_sns_client() -> Any:
    """Get SNS client."""
    try:
        client = boto3.client(
            "sns",
            region_name=config.aws.region,
            aws_access_key_id=config.aws.access_key_id,
            aws_secret_access_key=config.aws.secret_access_key,
            config=_get_boto3_config(),
        )
        logger.info("SNS client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize SNS client: {str(e)}")
        raise

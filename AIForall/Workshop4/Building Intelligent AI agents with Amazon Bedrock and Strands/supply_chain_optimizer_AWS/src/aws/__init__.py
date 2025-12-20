"""AWS services module for Supply Chain Optimizer."""

from .clients import (
    get_dynamodb_client,
    get_dynamodb_resource,
    get_eventbridge_client,
    get_lambda_client,
    get_rds_client,
    get_s3_client,
    get_sns_client,
)

__all__ = [
    "get_rds_client",
    "get_dynamodb_client",
    "get_dynamodb_resource",
    "get_s3_client",
    "get_lambda_client",
    "get_eventbridge_client",
    "get_sns_client",
]

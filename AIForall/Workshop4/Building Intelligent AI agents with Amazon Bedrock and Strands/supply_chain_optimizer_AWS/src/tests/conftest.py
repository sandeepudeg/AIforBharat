"""Pytest configuration and fixtures for Supply Chain Optimizer tests."""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
        },
    ):
        yield


@pytest.fixture
def mock_rds_client():
    """Mock RDS client."""
    with patch("src.aws.clients.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_dynamodb_client():
    """Mock DynamoDB client."""
    with patch("src.aws.clients.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_s3_client():
    """Mock S3 client."""
    with patch("src.aws.clients.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_sns_client():
    """Mock SNS client."""
    with patch("src.aws.clients.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_eventbridge_client():
    """Mock EventBridge client."""
    with patch("src.aws.clients.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_lambda_client():
    """Mock Lambda client."""
    with patch("src.aws.clients.boto3.client") as mock_client:
        yield mock_client


@pytest.fixture(autouse=True)
def mock_dynamodb_resource():
    """Mock DynamoDB resource for all tests."""
    mock_table = MagicMock()
    mock_table.put_item = MagicMock(return_value={"ResponseMetadata": {"HTTPStatusCode": 200}})
    mock_table.get_item = MagicMock(return_value={"Item": {}})
    mock_table.query = MagicMock(return_value={"Items": []})
    mock_table.scan = MagicMock(return_value={"Items": []})
    
    mock_resource = MagicMock()
    mock_resource.Table = MagicMock(return_value=mock_table)
    
    with patch("src.aws.clients.boto3.resource", return_value=mock_resource):
        yield mock_resource

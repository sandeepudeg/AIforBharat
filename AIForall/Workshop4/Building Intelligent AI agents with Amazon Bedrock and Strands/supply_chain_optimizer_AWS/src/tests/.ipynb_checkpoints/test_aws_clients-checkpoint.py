"""Tests for AWS service clients."""

from unittest.mock import MagicMock, patch

import pytest

from src.aws import (
    get_dynamodb_client,
    get_dynamodb_resource,
    get_eventbridge_client,
    get_lambda_client,
    get_rds_client,
    get_s3_client,
    get_sns_client,
)


@patch("src.aws.clients.boto3.client")
def test_get_rds_client(mock_boto3_client):
    """Test RDS client initialization."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    client = get_rds_client()

    assert client is not None
    mock_boto3_client.assert_called_once()
    call_args = mock_boto3_client.call_args
    assert call_args[0][0] == "rds"


@patch("src.aws.clients.boto3.client")
def test_get_dynamodb_client(mock_boto3_client):
    """Test DynamoDB client initialization."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    client = get_dynamodb_client()

    assert client is not None
    mock_boto3_client.assert_called_once()
    call_args = mock_boto3_client.call_args
    assert call_args[0][0] == "dynamodb"


@patch("src.aws.clients.boto3.resource")
def test_get_dynamodb_resource(mock_boto3_resource):
    """Test DynamoDB resource initialization."""
    mock_resource = MagicMock()
    mock_boto3_resource.return_value = mock_resource

    resource = get_dynamodb_resource()

    assert resource is not None
    mock_boto3_resource.assert_called_once()
    call_args = mock_boto3_resource.call_args
    assert call_args[0][0] == "dynamodb"


@patch("src.aws.clients.boto3.client")
def test_get_s3_client(mock_boto3_client):
    """Test S3 client initialization."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    client = get_s3_client()

    assert client is not None
    mock_boto3_client.assert_called_once()
    call_args = mock_boto3_client.call_args
    assert call_args[0][0] == "s3"


@patch("src.aws.clients.boto3.client")
def test_get_lambda_client(mock_boto3_client):
    """Test Lambda client initialization."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    client = get_lambda_client()

    assert client is not None
    mock_boto3_client.assert_called_once()
    call_args = mock_boto3_client.call_args
    assert call_args[0][0] == "lambda"


@patch("src.aws.clients.boto3.client")
def test_get_eventbridge_client(mock_boto3_client):
    """Test EventBridge client initialization."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    client = get_eventbridge_client()

    assert client is not None
    mock_boto3_client.assert_called_once()
    call_args = mock_boto3_client.call_args
    assert call_args[0][0] == "events"


@patch("src.aws.clients.boto3.client")
def test_get_sns_client(mock_boto3_client):
    """Test SNS client initialization."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    client = get_sns_client()

    assert client is not None
    mock_boto3_client.assert_called_once()
    call_args = mock_boto3_client.call_args
    assert call_args[0][0] == "sns"


@patch("src.aws.clients.boto3.client")
def test_get_rds_client_error_handling(mock_boto3_client):
    """Test RDS client error handling."""
    mock_boto3_client.side_effect = Exception("Connection failed")

    with pytest.raises(Exception):
        get_rds_client()


@patch("src.aws.clients.boto3.client")
def test_get_dynamodb_client_with_endpoint(mock_boto3_client):
    """Test DynamoDB client initialization with custom endpoint."""
    mock_client = MagicMock()
    mock_boto3_client.return_value = mock_client

    with patch("src.aws.clients.config") as mock_config:
        mock_config.dynamodb.endpoint = "http://localhost:8000"
        mock_config.dynamodb.region = "us-east-1"
        mock_config.aws.access_key_id = None
        mock_config.aws.secret_access_key = None

        client = get_dynamodb_client()

        assert client is not None
        call_kwargs = mock_boto3_client.call_args[1]
        assert call_kwargs.get("endpoint_url") == "http://localhost:8000"

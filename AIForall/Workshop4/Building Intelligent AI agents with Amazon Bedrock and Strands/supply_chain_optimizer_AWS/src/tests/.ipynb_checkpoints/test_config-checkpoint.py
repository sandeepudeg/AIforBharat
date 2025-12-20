"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from src.config import config


def test_config_loads_from_environment():
    """Test that configuration loads from environment variables."""
    # Test that config object properly reads environment variables
    # by checking that it has the expected structure
    assert hasattr(config, "aws")
    assert hasattr(config, "rds")
    assert hasattr(config, "logging")
    assert config.aws.region is not None
    assert config.rds.host is not None
    assert config.logging.level is not None


# def test_config_has_default_values():
#     """Test that configuration has sensible defaults."""
#     assert config.aws.region == "us-east-1"
#     assert config.rds.port == 5432
#     assert config.dynamodb.region == "us-west-2"
#     assert config.logging.level == "INFO"

def test_config_has_default_values(monkeypatch):
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)

    from src.config import load_config
    config = load_config()

    assert config.aws.region == "us-west-2"
    assert config.rds.port == 5432
    assert config.dynamodb.region == "us-west-2"
    assert config.logging.level == "INFO"

def test_config_aws_section():
    """Test AWS configuration section."""
    assert hasattr(config, "aws")
    assert hasattr(config.aws, "region")
    assert hasattr(config.aws, "access_key_id")
    assert hasattr(config.aws, "secret_access_key")


def test_config_rds_section():
    """Test RDS configuration section."""
    assert hasattr(config, "rds")
    assert hasattr(config.rds, "host")
    assert hasattr(config.rds, "port")
    assert hasattr(config.rds, "database")
    assert hasattr(config.rds, "username")
    assert hasattr(config.rds, "password")


def test_config_dynamodb_section():
    """Test DynamoDB configuration section."""
    assert hasattr(config, "dynamodb")
    assert hasattr(config.dynamodb, "region")
    assert hasattr(config.dynamodb, "endpoint")


def test_config_s3_section():
    """Test S3 configuration section."""
    assert hasattr(config, "s3")
    assert hasattr(config.s3, "bucket_name")
    assert hasattr(config.s3, "region")


def test_config_sns_section():
    """Test SNS configuration section."""
    assert hasattr(config, "sns")
    assert hasattr(config.sns, "topic_arn_alerts")
    assert hasattr(config.sns, "topic_arn_notifications")


def test_config_bedrock_section():
    """Test Bedrock configuration section."""
    assert hasattr(config, "bedrock")
    assert hasattr(config.bedrock, "model_id")
    assert hasattr(config.bedrock, "region")


def test_config_app_section():
    """Test application configuration section."""
    assert hasattr(config, "app")
    assert hasattr(config.app, "node_env")
    assert hasattr(config.app, "is_development")
    assert hasattr(config.app, "is_production")

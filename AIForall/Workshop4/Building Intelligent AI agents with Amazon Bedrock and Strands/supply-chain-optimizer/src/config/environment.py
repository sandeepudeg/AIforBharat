"""Environment configuration for Supply Chain Optimizer."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class AWSConfig(BaseSettings):
    """AWS configuration."""

    region: str = os.getenv("AWS_REGION", "us-east-1")
    access_key_id: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    secret_access_key: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")


class RDSConfig(BaseSettings):
    """RDS configuration."""

    host: str = os.getenv("RDS_HOST", "localhost")
    port: int = int(os.getenv("RDS_PORT", "5432"))
    database: str = os.getenv("RDS_DATABASE", "supply_chain_db")
    username: str = os.getenv("RDS_USERNAME", "postgres")
    password: str = os.getenv("RDS_PASSWORD", "")


class DynamoDBConfig(BaseSettings):
    """DynamoDB configuration."""

    region: str = os.getenv("DYNAMODB_REGION", "us-east-1")
    endpoint: Optional[str] = os.getenv("DYNAMODB_ENDPOINT")


class S3Config(BaseSettings):
    """S3 configuration."""

    bucket_name: str = os.getenv("S3_BUCKET_NAME", "supply-chain-optimizer-reports")
    region: str = os.getenv("S3_REGION", "us-east-1")


class SNSConfig(BaseSettings):
    """SNS configuration."""

    topic_arn_alerts: str = os.getenv("SNS_TOPIC_ARN_ALERTS", "")
    topic_arn_notifications: str = os.getenv("SNS_TOPIC_ARN_NOTIFICATIONS", "")


class LambdaConfig(BaseSettings):
    """Lambda configuration."""

    role_arn: str = os.getenv("LAMBDA_ROLE_ARN", "")


class EventBridgeConfig(BaseSettings):
    """EventBridge configuration."""

    rule_name: str = os.getenv("EVENTBRIDGE_RULE_NAME", "supply-chain-events")


class LoggingConfig(BaseSettings):
    """Logging configuration."""

    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "json")


class BedrockConfig(BaseSettings):
    """Bedrock configuration."""

    model_id: str = os.getenv(
        "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
    )
    region: str = os.getenv("BEDROCK_REGION", "us-east-1")


class AppConfig(BaseSettings):
    """Application configuration."""

    node_env: str = os.getenv("NODE_ENV", "development")
    is_development: bool = os.getenv("NODE_ENV", "development") == "development"
    is_production: bool = os.getenv("NODE_ENV", "development") == "production"


class Config(BaseSettings):
    """Main configuration class."""

    aws: AWSConfig = AWSConfig()
    rds: RDSConfig = RDSConfig()
    dynamodb: DynamoDBConfig = DynamoDBConfig()
    s3: S3Config = S3Config()
    sns: SNSConfig = SNSConfig()
    lambda_config: LambdaConfig = LambdaConfig()
    event_bridge: EventBridgeConfig = EventBridgeConfig()
    logging: LoggingConfig = LoggingConfig()
    bedrock: BedrockConfig = BedrockConfig()
    app: AppConfig = AppConfig()


config = Config()

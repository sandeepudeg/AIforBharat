"""Database connection utilities."""

from typing import Any, Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from src.config import config, logger


_rds_engine: Optional[Engine] = None
_session_maker: Optional[sessionmaker] = None


def get_rds_connection() -> Engine:
    """Get or create RDS connection engine."""
    global _rds_engine

    if _rds_engine is not None:
        return _rds_engine

    try:
        # Build connection string
        connection_string = (
            f"postgresql://{config.rds.username}:{config.rds.password}"
            f"@{config.rds.host}:{config.rds.port}/{config.rds.database}"
        )

        # Create engine with connection pooling
        _rds_engine = create_engine(
            connection_string,
            echo=config.app.is_development,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        logger.info("RDS connection engine created successfully")
        return _rds_engine

    except Exception as e:
        logger.error(f"Failed to create RDS connection: {str(e)}")
        raise


def get_rds_session() -> Session:
    """Get a new RDS database session."""
    global _session_maker

    if _session_maker is None:
        engine = get_rds_connection()
        _session_maker = sessionmaker(bind=engine)

    return _session_maker()


def close_rds_connection() -> None:
    """Close RDS connection engine."""
    global _rds_engine

    if _rds_engine is not None:
        _rds_engine.dispose()
        _rds_engine = None
        logger.info("RDS connection closed")


def get_dynamodb_connection() -> Any:
    """Get DynamoDB resource for table operations."""
    try:
        import boto3

        kwargs = {
            "region_name": config.dynamodb.region,
            "aws_access_key_id": config.aws.access_key_id,
            "aws_secret_access_key": config.aws.secret_access_key,
        }

        if config.dynamodb.endpoint:
            kwargs["endpoint_url"] = config.dynamodb.endpoint

        resource = boto3.resource("dynamodb", **kwargs)
        logger.info("DynamoDB connection established")
        return resource

    except Exception as e:
        logger.error(f"Failed to create DynamoDB connection: {str(e)}")
        raise

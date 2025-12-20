"""Tests for database connection and schema."""

from unittest.mock import patch, MagicMock

import pytest

from src.database.connection import (
    get_rds_connection,
    get_rds_session,
    close_rds_connection,
    get_dynamodb_connection,
)


class TestRDSConnection:
    """Tests for RDS connection."""

    def test_get_rds_connection_creates_engine(self):
        """Test that get_rds_connection creates an engine."""
        # Reset the global engine
        import src.database.connection as conn_module

        conn_module._rds_engine = None

        with patch("src.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            engine = get_rds_connection()

            assert engine is not None
            mock_create.assert_called_once()

    def test_get_rds_connection_reuses_engine(self):
        """Test that get_rds_connection reuses existing engine."""
        import src.database.connection as conn_module

        # Create a mock engine
        mock_engine = MagicMock()
        conn_module._rds_engine = mock_engine

        engine = get_rds_connection()

        assert engine is mock_engine

    def test_close_rds_connection(self):
        """Test closing RDS connection."""
        import src.database.connection as conn_module

        mock_engine = MagicMock()
        conn_module._rds_engine = mock_engine

        close_rds_connection()

        mock_engine.dispose.assert_called_once()
        assert conn_module._rds_engine is None

    def test_get_rds_session(self):
        """Test getting RDS session."""
        import src.database.connection as conn_module

        conn_module._rds_engine = None
        conn_module._session_maker = None

        with patch("src.database.connection.create_engine") as mock_create:
            mock_engine = MagicMock()
            mock_create.return_value = mock_engine

            with patch("src.database.connection.sessionmaker") as mock_sessionmaker:
                mock_session_factory = MagicMock()
                mock_sessionmaker.return_value = mock_session_factory
                mock_session = MagicMock()
                mock_session_factory.return_value = mock_session

                session = get_rds_session()

                assert session is mock_session


class TestDynamoDBConnection:
    """Tests for DynamoDB connection."""

    def test_get_dynamodb_connection(self):
        """Test getting DynamoDB connection."""
        with patch("boto3.resource") as mock_resource:
            mock_dynamodb = MagicMock()
            mock_resource.return_value = mock_dynamodb

            dynamodb = get_dynamodb_connection()

            assert dynamodb is mock_dynamodb
            mock_resource.assert_called_once()

    def test_get_dynamodb_connection_with_endpoint(self):
        """Test getting DynamoDB connection with custom endpoint."""
        with patch("src.database.connection.config") as mock_config:
            mock_config.dynamodb.region = "us-east-1"
            mock_config.dynamodb.endpoint = "http://localhost:8000"
            mock_config.aws.access_key_id = "test"
            mock_config.aws.secret_access_key = "test"

            with patch("boto3.resource") as mock_resource:
                mock_dynamodb = MagicMock()
                mock_resource.return_value = mock_dynamodb

                dynamodb = get_dynamodb_connection()

                assert dynamodb is mock_dynamodb
                # Verify endpoint_url was passed
                call_kwargs = mock_resource.call_args[1]
                assert call_kwargs.get("endpoint_url") == "http://localhost:8000"


class TestDatabaseSchema:
    """Tests for database schema creation."""

    def test_create_rds_schema(self):
        """Test creating RDS schema."""
        from src.database.schema import create_rds_schema

        with patch("src.database.schema.get_rds_connection") as mock_get_conn:
            mock_engine = MagicMock()
            mock_get_conn.return_value = mock_engine

            with patch("src.database.schema.Base.metadata") as mock_metadata:
                create_rds_schema()

                mock_metadata.create_all.assert_called_once_with(mock_engine)

    def test_drop_rds_schema(self):
        """Test dropping RDS schema."""
        from src.database.schema import drop_rds_schema

        with patch("src.database.schema.get_rds_connection") as mock_get_conn:
            mock_engine = MagicMock()
            mock_get_conn.return_value = mock_engine

            with patch("src.database.schema.Base.metadata") as mock_metadata:
                drop_rds_schema()

                mock_metadata.drop_all.assert_called_once_with(mock_engine)

    def test_create_dynamodb_tables(self):
        """Test creating DynamoDB tables."""
        from src.database.schema import create_dynamodb_tables

        with patch("src.database.schema.get_dynamodb_connection") as mock_get_conn:
            mock_dynamodb = MagicMock()
            mock_get_conn.return_value = mock_dynamodb

            create_dynamodb_tables()

            # Verify create_table was called for each table
            assert mock_dynamodb.create_table.call_count >= 3

    def test_drop_dynamodb_tables(self):
        """Test dropping DynamoDB tables."""
        from src.database.schema import drop_dynamodb_tables

        with patch("src.database.schema.get_dynamodb_connection") as mock_get_conn:
            mock_dynamodb = MagicMock()
            mock_table = MagicMock()
            mock_dynamodb.Table.return_value = mock_table
            mock_get_conn.return_value = mock_dynamodb

            drop_dynamodb_tables()

            # Verify Table was called for each table
            assert mock_dynamodb.Table.call_count >= 3

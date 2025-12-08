"""Tests for Error Handling"""

import pytest
from datetime import datetime
from src.error_handler import (
    ErrorHandler,
    ErrorLog,
    IngestionSummary,
    ErrorSeverity,
    DocumentProcessingError,
    MalformedDocumentError,
    IngestionError,
    APIError,
    KnowledgeBaseUnavailableError,
    RateLimitError
)


class TestErrorLog:
    """Tests for ErrorLog class"""

    def test_error_log_creation(self):
        """Test creating an error log"""
        error_log = ErrorLog(
            error_type="TestError",
            message="Test error message",
            severity=ErrorSeverity.ERROR,
            context={"key": "value"}
        )

        assert error_log.error_type == "TestError"
        assert error_log.message == "Test error message"
        assert error_log.severity == ErrorSeverity.ERROR
        assert error_log.context == {"key": "value"}
        assert error_log.timestamp is not None

    def test_error_log_to_dict(self):
        """Test converting error log to dictionary"""
        error_log = ErrorLog(
            error_type="TestError",
            message="Test error message",
            severity=ErrorSeverity.WARNING,
            context={"document_id": "doc-123"}
        )

        result = error_log.to_dict()

        assert result["error_type"] == "TestError"
        assert result["message"] == "Test error message"
        assert result["severity"] == "WARNING"
        assert result["context"]["document_id"] == "doc-123"
        assert "timestamp" in result

    def test_error_log_default_timestamp(self):
        """Test error log uses current timestamp by default"""
        before = datetime.utcnow()
        error_log = ErrorLog(
            error_type="TestError",
            message="Test",
            severity=ErrorSeverity.INFO
        )
        after = datetime.utcnow()

        assert before <= error_log.timestamp <= after

    def test_error_log_custom_timestamp(self):
        """Test error log with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        error_log = ErrorLog(
            error_type="TestError",
            message="Test",
            severity=ErrorSeverity.INFO,
            timestamp=custom_time
        )

        assert error_log.timestamp == custom_time


class TestIngestionSummary:
    """Tests for IngestionSummary class"""

    def test_ingestion_summary_creation(self):
        """Test creating an ingestion summary"""
        summary = IngestionSummary()

        assert summary.total_documents == 0
        assert summary.successful_documents == 0
        assert summary.failed_documents == 0
        assert len(summary.error_logs) == 0

    def test_ingestion_summary_add_error(self):
        """Test adding errors to ingestion summary"""
        summary = IngestionSummary()

        summary.add_error(
            error_type="MalformedDocument",
            message="Document is malformed",
            severity=ErrorSeverity.WARNING,
            context={"document_id": "doc-1"}
        )

        assert len(summary.error_logs) == 1
        assert summary.error_logs[0].error_type == "MalformedDocument"

    def test_ingestion_summary_success_rate(self):
        """Test calculating success rate"""
        summary = IngestionSummary()
        summary.total_documents = 100
        summary.successful_documents = 95
        summary.failed_documents = 5

        assert summary.get_success_rate() == 95.0

    def test_ingestion_summary_success_rate_zero_documents(self):
        """Test success rate with zero documents"""
        summary = IngestionSummary()

        assert summary.get_success_rate() == 0.0

    def test_ingestion_summary_failure_rate(self):
        """Test calculating failure rate"""
        summary = IngestionSummary()
        summary.total_documents = 100
        summary.successful_documents = 95
        summary.failed_documents = 5

        assert summary.get_failure_rate() == 5.0

    def test_ingestion_summary_duration(self):
        """Test calculating ingestion duration"""
        summary = IngestionSummary()
        summary.start_time = datetime(2024, 1, 1, 12, 0, 0)
        summary.end_time = datetime(2024, 1, 1, 12, 10, 0)

        assert summary.get_duration_seconds() == 600.0

    def test_ingestion_summary_duration_not_completed(self):
        """Test duration when ingestion not completed"""
        summary = IngestionSummary()
        summary.start_time = datetime(2024, 1, 1, 12, 0, 0)

        assert summary.get_duration_seconds() is None

    def test_ingestion_summary_to_dict(self):
        """Test converting ingestion summary to dictionary"""
        summary = IngestionSummary()
        summary.total_documents = 100
        summary.successful_documents = 95
        summary.failed_documents = 5
        summary.start_time = datetime(2024, 1, 1, 12, 0, 0)
        summary.end_time = datetime(2024, 1, 1, 12, 10, 0)

        summary.add_error(
            error_type="IngestionError",
            message="Failed to ingest document",
            severity=ErrorSeverity.ERROR
        )

        result = summary.to_dict()

        assert result["total_documents"] == 100
        assert result["successful_documents"] == 95
        assert result["failed_documents"] == 5
        assert result["success_rate_percent"] == 95.0
        assert result["failure_rate_percent"] == 5.0
        assert result["duration_seconds"] == 600.0
        assert result["error_count"] == 1


class TestErrorHandler:
    """Tests for ErrorHandler class"""

    def test_error_handler_creation(self):
        """Test creating an error handler"""
        handler = ErrorHandler()

        assert handler.logger is not None
        assert len(handler.error_logs) == 0

    def test_error_handler_handle_malformed_document(self):
        """Test handling malformed document"""
        handler = ErrorHandler()

        handler.handle_malformed_document(
            document_id="doc-1",
            error_message="Missing required field",
            document_content="<invalid>"
        )

        assert len(handler.error_logs) == 1
        assert handler.error_logs[0].error_type == "MalformedDocument"
        assert "doc-1" in handler.error_logs[0].message

    def test_error_handler_handle_ingestion_error(self):
        """Test handling ingestion error"""
        handler = ErrorHandler()

        handler.handle_ingestion_error(
            document_id="doc-1",
            error_message="Failed to parse document",
            error_type="ParsingError"
        )

        assert len(handler.error_logs) == 1
        assert handler.error_logs[0].error_type == "ParsingError"
        assert handler.error_logs[0].severity == ErrorSeverity.ERROR

    def test_error_handler_handle_api_error_retryable(self):
        """Test handling retryable API error"""
        handler = ErrorHandler()

        handler.handle_api_error(
            operation="StartIngestionJob",
            error_message="Service temporarily unavailable",
            error_code="ServiceUnavailable",
            is_retryable=True
        )

        assert len(handler.error_logs) == 1
        assert handler.error_logs[0].error_type == "APIError"
        assert handler.error_logs[0].severity == ErrorSeverity.WARNING
        assert handler.error_logs[0].context["is_retryable"] is True

    def test_error_handler_handle_api_error_not_retryable(self):
        """Test handling non-retryable API error"""
        handler = ErrorHandler()

        handler.handle_api_error(
            operation="GetIngestionJob",
            error_message="Access denied",
            error_code="AccessDenied",
            is_retryable=False
        )

        assert len(handler.error_logs) == 1
        assert handler.error_logs[0].severity == ErrorSeverity.ERROR

    def test_error_handler_handle_knowledge_base_unavailable(self):
        """Test handling knowledge base unavailability"""
        handler = ErrorHandler()

        handler.handle_knowledge_base_unavailable(
            kb_id="kb-123",
            reason="Knowledge base is being updated"
        )

        assert len(handler.error_logs) == 1
        assert handler.error_logs[0].error_type == "KnowledgeBaseUnavailable"
        assert handler.error_logs[0].severity == ErrorSeverity.CRITICAL

    def test_error_handler_handle_rate_limit(self):
        """Test handling rate limit error"""
        handler = ErrorHandler()

        handler.handle_rate_limit(
            operation="RetrieveAPI",
            retry_after_seconds=60
        )

        assert len(handler.error_logs) == 1
        assert handler.error_logs[0].error_type == "RateLimit"
        assert handler.error_logs[0].severity == ErrorSeverity.WARNING
        assert handler.error_logs[0].context["retry_after_seconds"] == 60

    def test_error_handler_get_error_logs(self):
        """Test retrieving error logs"""
        handler = ErrorHandler()

        handler.handle_malformed_document("doc-1", "Error 1")
        handler.handle_ingestion_error("doc-2", "Error 2")

        logs = handler.get_error_logs()

        assert len(logs) == 2

    def test_error_handler_get_errors_by_severity(self):
        """Test filtering errors by severity"""
        handler = ErrorHandler()

        handler.handle_malformed_document("doc-1", "Warning error")
        handler.handle_api_error("op", "Error", is_retryable=False)
        handler.handle_knowledge_base_unavailable("kb-1", "Critical error")

        critical_errors = handler.get_errors_by_severity(ErrorSeverity.CRITICAL)
        warning_errors = handler.get_errors_by_severity(ErrorSeverity.WARNING)

        assert len(critical_errors) == 1
        assert len(warning_errors) == 1

    def test_error_handler_get_errors_by_type(self):
        """Test filtering errors by type"""
        handler = ErrorHandler()

        handler.handle_malformed_document("doc-1", "Error 1")
        handler.handle_malformed_document("doc-2", "Error 2")
        handler.handle_ingestion_error("doc-3", "Error 3")

        malformed_errors = handler.get_errors_by_type("MalformedDocument")
        ingestion_errors = handler.get_errors_by_type("IngestionError")

        assert len(malformed_errors) == 2
        assert len(ingestion_errors) == 1

    def test_error_handler_clear_error_logs(self):
        """Test clearing error logs"""
        handler = ErrorHandler()

        handler.handle_malformed_document("doc-1", "Error")
        assert len(handler.error_logs) == 1

        handler.clear_error_logs()
        assert len(handler.error_logs) == 0

    def test_error_handler_get_error_summary(self):
        """Test getting error summary"""
        handler = ErrorHandler()

        handler.handle_malformed_document("doc-1", "Error 1")
        handler.handle_malformed_document("doc-2", "Error 2")
        handler.handle_api_error("op", "Error 3", is_retryable=False)
        handler.handle_knowledge_base_unavailable("kb-1", "Error 4")

        summary = handler.get_error_summary()

        assert summary["total_errors"] == 4
        assert summary["critical_errors"] == 1
        assert summary["error_errors"] == 1
        assert summary["warning_errors"] == 2
        assert "MalformedDocument" in summary["errors_by_type"]
        assert summary["errors_by_type"]["MalformedDocument"] == 2


class TestExceptionClasses:
    """Tests for custom exception classes"""

    def test_document_processing_error(self):
        """Test DocumentProcessingError exception"""
        with pytest.raises(DocumentProcessingError):
            raise DocumentProcessingError("Test error")

    def test_malformed_document_error(self):
        """Test MalformedDocumentError exception"""
        with pytest.raises(MalformedDocumentError):
            raise MalformedDocumentError("Document is malformed")

    def test_ingestion_error(self):
        """Test IngestionError exception"""
        with pytest.raises(IngestionError):
            raise IngestionError("Ingestion failed")

    def test_api_error(self):
        """Test APIError exception"""
        with pytest.raises(APIError):
            raise APIError("API call failed")

    def test_knowledge_base_unavailable_error(self):
        """Test KnowledgeBaseUnavailableError exception"""
        with pytest.raises(KnowledgeBaseUnavailableError):
            raise KnowledgeBaseUnavailableError("KB is unavailable")

    def test_rate_limit_error(self):
        """Test RateLimitError exception"""
        with pytest.raises(RateLimitError):
            raise RateLimitError("Rate limit exceeded")

    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy"""
        assert issubclass(MalformedDocumentError, DocumentProcessingError)
        assert issubclass(IngestionError, DocumentProcessingError)
        assert issubclass(APIError, DocumentProcessingError)
        assert issubclass(KnowledgeBaseUnavailableError, DocumentProcessingError)
        assert issubclass(RateLimitError, DocumentProcessingError)

"""Error handling and logging for Bedrock RAG Retrieval System"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DocumentProcessingError(Exception):
    """Base exception for document processing errors"""
    pass


class MalformedDocumentError(DocumentProcessingError):
    """Exception raised when a document is malformed"""
    pass


class IngestionError(DocumentProcessingError):
    """Exception raised during document ingestion"""
    pass


class APIError(DocumentProcessingError):
    """Exception raised when API calls fail"""
    pass


class KnowledgeBaseUnavailableError(DocumentProcessingError):
    """Exception raised when knowledge base is unavailable"""
    pass


class RateLimitError(DocumentProcessingError):
    """Exception raised when rate limits are exceeded"""
    pass


class ErrorLog:
    """Represents a single error log entry"""

    def __init__(
        self,
        error_type: str,
        message: str,
        severity: ErrorSeverity,
        context: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize error log entry.

        Args:
            error_type: Type of error (e.g., 'MalformedDocument', 'APIError')
            message: Error message
            severity: Severity level of the error
            context: Additional context information
            timestamp: Timestamp of the error (defaults to now)
        """
        self.error_type = error_type
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error log to dictionary"""
        return {
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity.value,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }


class IngestionSummary:
    """Summary of ingestion results including errors"""

    def __init__(self):
        """Initialize ingestion summary"""
        self.total_documents = 0
        self.successful_documents = 0
        self.failed_documents = 0
        self.error_logs: List[ErrorLog] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def add_error(
        self,
        error_type: str,
        message: str,
        severity: ErrorSeverity,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an error to the summary.

        Args:
            error_type: Type of error
            message: Error message
            severity: Severity level
            context: Additional context
        """
        error_log = ErrorLog(error_type, message, severity, context)
        self.error_logs.append(error_log)

    def get_success_rate(self) -> float:
        """
        Get the success rate as a percentage.

        Returns:
            Success rate (0-100), or 0 if no documents processed
        """
        if self.total_documents == 0:
            return 0.0
        return (self.successful_documents / self.total_documents) * 100

    def get_failure_rate(self) -> float:
        """
        Get the failure rate as a percentage.

        Returns:
            Failure rate (0-100), or 0 if no documents processed
        """
        if self.total_documents == 0:
            return 0.0
        return (self.failed_documents / self.total_documents) * 100

    def get_duration_seconds(self) -> Optional[float]:
        """
        Get the duration of ingestion in seconds.

        Returns:
            Duration in seconds, or None if not completed
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary"""
        return {
            "total_documents": self.total_documents,
            "successful_documents": self.successful_documents,
            "failed_documents": self.failed_documents,
            "success_rate_percent": self.get_success_rate(),
            "failure_rate_percent": self.get_failure_rate(),
            "duration_seconds": self.get_duration_seconds(),
            "error_count": len(self.error_logs),
            "errors": [error.to_dict() for error in self.error_logs]
        }


class ErrorHandler:
    """Handles errors and logging for the RAG system"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler.

        Args:
            logger: Optional logger instance (creates default if not provided)
        """
        self.logger = logger or self._create_default_logger()
        self.error_logs: List[ErrorLog] = []

    @staticmethod
    def _create_default_logger() -> logging.Logger:
        """Create a default logger"""
        logger = logging.getLogger("bedrock_rag_error_handler")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def handle_malformed_document(
        self,
        document_id: str,
        error_message: str,
        document_content: Optional[str] = None
    ) -> None:
        """
        Handle a malformed document error.

        Args:
            document_id: ID of the malformed document
            error_message: Description of what's wrong with the document
            document_content: Optional content of the document for debugging
        """
        context = {
            "document_id": document_id,
            "content_preview": (
                document_content[:100] if document_content else None
            )
        }

        error_log = ErrorLog(
            error_type="MalformedDocument",
            message=f"Document {document_id} is malformed: {error_message}",
            severity=ErrorSeverity.WARNING,
            context=context
        )

        self.error_logs.append(error_log)
        self.logger.warning(
            f"Malformed document skipped: {document_id} - {error_message}"
        )

    def handle_ingestion_error(
        self,
        document_id: str,
        error_message: str,
        error_type: str = "IngestionError"
    ) -> None:
        """
        Handle an ingestion error.

        Args:
            document_id: ID of the document that failed ingestion
            error_message: Description of the ingestion error
            error_type: Type of ingestion error
        """
        context = {"document_id": document_id}

        error_log = ErrorLog(
            error_type=error_type,
            message=f"Failed to ingest document {document_id}: {error_message}",
            severity=ErrorSeverity.ERROR,
            context=context
        )

        self.error_logs.append(error_log)
        self.logger.error(
            f"Ingestion failed for document {document_id}: {error_message}"
        )

    def handle_api_error(
        self,
        operation: str,
        error_message: str,
        error_code: Optional[str] = None,
        is_retryable: bool = False
    ) -> None:
        """
        Handle an API error.

        Args:
            operation: Name of the operation that failed
            error_message: Description of the API error
            error_code: Optional error code from the API
            is_retryable: Whether the error is retryable
        """
        context = {
            "operation": operation,
            "error_code": error_code,
            "is_retryable": is_retryable
        }

        severity = ErrorSeverity.WARNING if is_retryable else ErrorSeverity.ERROR

        error_log = ErrorLog(
            error_type="APIError",
            message=f"API error during {operation}: {error_message}",
            severity=severity,
            context=context
        )

        self.error_logs.append(error_log)

        log_message = (
            f"API error during {operation}: {error_message}"
        )
        if error_code:
            log_message += f" (Code: {error_code})"
        if is_retryable:
            log_message += " [RETRYABLE]"

        if is_retryable:
            self.logger.warning(log_message)
        else:
            self.logger.error(log_message)

    def handle_knowledge_base_unavailable(
        self,
        kb_id: str,
        reason: str
    ) -> None:
        """
        Handle knowledge base unavailability.

        Args:
            kb_id: ID of the unavailable knowledge base
            reason: Reason for unavailability
        """
        context = {"kb_id": kb_id}

        error_log = ErrorLog(
            error_type="KnowledgeBaseUnavailable",
            message=f"Knowledge base {kb_id} is unavailable: {reason}",
            severity=ErrorSeverity.CRITICAL,
            context=context
        )

        self.error_logs.append(error_log)
        self.logger.critical(
            f"Knowledge base {kb_id} is unavailable: {reason}"
        )

    def handle_rate_limit(
        self,
        operation: str,
        retry_after_seconds: Optional[int] = None
    ) -> None:
        """
        Handle rate limit error.

        Args:
            operation: Name of the operation that hit rate limit
            retry_after_seconds: Optional seconds to wait before retry
        """
        context = {
            "operation": operation,
            "retry_after_seconds": retry_after_seconds
        }

        error_log = ErrorLog(
            error_type="RateLimit",
            message=f"Rate limit exceeded for {operation}",
            severity=ErrorSeverity.WARNING,
            context=context
        )

        self.error_logs.append(error_log)

        log_message = f"Rate limit exceeded for {operation}"
        if retry_after_seconds:
            log_message += f" - retry after {retry_after_seconds} seconds"

        self.logger.warning(log_message)

    def get_error_logs(self) -> List[ErrorLog]:
        """
        Get all error logs.

        Returns:
            List of error logs
        """
        return self.error_logs.copy()

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorLog]:
        """
        Get error logs filtered by severity.

        Args:
            severity: Severity level to filter by

        Returns:
            List of error logs with the specified severity
        """
        return [log for log in self.error_logs if log.severity == severity]

    def get_errors_by_type(self, error_type: str) -> List[ErrorLog]:
        """
        Get error logs filtered by error type.

        Args:
            error_type: Error type to filter by

        Returns:
            List of error logs with the specified type
        """
        return [log for log in self.error_logs if log.error_type == error_type]

    def clear_error_logs(self) -> None:
        """Clear all error logs"""
        self.error_logs.clear()

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all errors.

        Returns:
            Dictionary containing error summary statistics
        """
        total_errors = len(self.error_logs)
        errors_by_severity = {}
        errors_by_type = {}

        for log in self.error_logs:
            severity = log.severity.value
            error_type = log.error_type

            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        return {
            "total_errors": total_errors,
            "errors_by_severity": errors_by_severity,
            "errors_by_type": errors_by_type,
            "critical_errors": len(self.get_errors_by_severity(ErrorSeverity.CRITICAL)),
            "error_errors": len(self.get_errors_by_severity(ErrorSeverity.ERROR)),
            "warning_errors": len(self.get_errors_by_severity(ErrorSeverity.WARNING)),
            "info_errors": len(self.get_errors_by_severity(ErrorSeverity.INFO))
        }

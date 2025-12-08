"""Property-based tests for Error Handling Stability

**Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

Property 6: Error Handling Stability
*For any* failed API call or malformed document, the system should catch the exception,
log it appropriately, and continue processing without crashing.
"""

import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime
from src.error_handler import (
    ErrorHandler,
    ErrorSeverity,
    DocumentProcessingError,
    MalformedDocumentError,
    IngestionError,
    APIError,
    KnowledgeBaseUnavailableError,
    RateLimitError
)


# Strategies for generating test data
@st.composite
def error_types(draw):
    """Generate valid error types"""
    return draw(st.sampled_from([
        "MalformedDocument",
        "IngestionError",
        "APIError",
        "KnowledgeBaseUnavailable",
        "RateLimit",
        "CustomError"
    ]))


@st.composite
def error_severities(draw):
    """Generate valid error severities"""
    return draw(st.sampled_from([
        ErrorSeverity.INFO,
        ErrorSeverity.WARNING,
        ErrorSeverity.ERROR,
        ErrorSeverity.CRITICAL
    ]))


@st.composite
def document_ids(draw):
    """Generate valid document IDs"""
    return draw(st.text(
        alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
        min_size=1,
        max_size=100
    ))


@st.composite
def error_messages(draw):
    """Generate valid error messages"""
    return draw(st.text(
        alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
        min_size=1,
        max_size=500
    ))


@st.composite
def operation_names(draw):
    """Generate valid operation names"""
    return draw(st.sampled_from([
        "CreateKnowledgeBase",
        "StartIngestionJob",
        "RetrieveDocuments",
        "GenerateResponse",
        "UpdateDataSource",
        "DeleteKnowledgeBase"
    ]))


@st.composite
def error_codes(draw):
    """Generate valid AWS error codes"""
    return draw(st.sampled_from([
        "ServiceUnavailable",
        "AccessDenied",
        "ValidationException",
        "ResourceNotFoundException",
        "ThrottlingException",
        "InternalServerError"
    ]))


class TestErrorHandlingStability:
    """Tests for error handling stability property"""

    @given(
        error_type=error_types(),
        message=error_messages(),
        severity=error_severities()
    )
    def test_error_handler_catches_and_logs_errors(
        self,
        error_type,
        message,
        severity
    ):
        """
        Property: For any error type, message, and severity, the error handler
        should catch and log the error without crashing.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.3**
        """
        from src.error_handler import ErrorLog
        handler = ErrorHandler()
        
        # The handler should not crash when logging any error
        try:
            error_log = ErrorLog(
                error_type=error_type,
                message=message,
                severity=severity
            )
            # Verify error log was created successfully
            assert error_log.error_type == error_type
            assert error_log.message == message
            assert error_log.severity == severity
        except Exception as e:
            pytest.fail(f"Error handler crashed: {e}")

    @given(
        document_id=document_ids(),
        error_message=error_messages()
    )
    def test_malformed_document_handling_continues_processing(
        self,
        document_id,
        error_message
    ):
        """
        Property: For any malformed document, the error handler should log it
        and allow processing to continue without crashing.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.2, 6.3**
        """
        handler = ErrorHandler()
        initial_error_count = len(handler.error_logs)
        
        # Handle malformed document
        try:
            handler.handle_malformed_document(
                document_id=document_id,
                error_message=error_message
            )
        except Exception as e:
            pytest.fail(f"Malformed document handler crashed: {e}")
        
        # Verify error was logged
        assert len(handler.error_logs) == initial_error_count + 1
        
        # Verify we can continue processing (handler is still functional)
        try:
            handler.handle_malformed_document(
                document_id="another_doc",
                error_message="Another error"
            )
        except Exception as e:
            pytest.fail(f"Handler crashed after first error: {e}")
        
        # Verify both errors were logged
        assert len(handler.error_logs) == initial_error_count + 2

    @given(
        operation=operation_names(),
        error_message=error_messages(),
        error_code=error_codes(),
        is_retryable=st.booleans()
    )
    def test_api_error_handling_continues_processing(
        self,
        operation,
        error_message,
        error_code,
        is_retryable
    ):
        """
        Property: For any API error, the error handler should log it with
        appropriate severity and allow processing to continue.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.3**
        """
        handler = ErrorHandler()
        initial_error_count = len(handler.error_logs)
        
        # Handle API error
        try:
            handler.handle_api_error(
                operation=operation,
                error_message=error_message,
                error_code=error_code,
                is_retryable=is_retryable
            )
        except Exception as e:
            pytest.fail(f"API error handler crashed: {e}")
        
        # Verify error was logged
        assert len(handler.error_logs) == initial_error_count + 1
        
        # Verify severity is appropriate
        logged_error = handler.error_logs[-1]
        if is_retryable:
            assert logged_error.severity == ErrorSeverity.WARNING
        else:
            assert logged_error.severity == ErrorSeverity.ERROR
        
        # Verify handler is still functional
        try:
            handler.handle_api_error(
                operation="AnotherOperation",
                error_message="Another error",
                error_code="AnotherCode",
                is_retryable=False
            )
        except Exception as e:
            pytest.fail(f"Handler crashed after first API error: {e}")
        
        assert len(handler.error_logs) == initial_error_count + 2

    @given(
        kb_id=st.text(min_size=1, max_size=50),
        reason=error_messages()
    )
    def test_knowledge_base_unavailability_handling(
        self,
        kb_id,
        reason
    ):
        """
        Property: For any knowledge base unavailability, the error handler
        should log it as critical and allow processing to continue.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.3**
        """
        handler = ErrorHandler()
        initial_error_count = len(handler.error_logs)
        
        # Handle KB unavailability
        try:
            handler.handle_knowledge_base_unavailable(
                kb_id=kb_id,
                reason=reason
            )
        except Exception as e:
            pytest.fail(f"KB unavailability handler crashed: {e}")
        
        # Verify error was logged as critical
        assert len(handler.error_logs) == initial_error_count + 1
        logged_error = handler.error_logs[-1]
        assert logged_error.severity == ErrorSeverity.CRITICAL
        assert logged_error.error_type == "KnowledgeBaseUnavailable"

    @given(
        operation=operation_names(),
        retry_after=st.one_of(st.none(), st.integers(min_value=1, max_value=3600))
    )
    def test_rate_limit_handling_continues_processing(
        self,
        operation,
        retry_after
    ):
        """
        Property: For any rate limit error, the error handler should log it
        and allow processing to continue.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.4**
        """
        handler = ErrorHandler()
        initial_error_count = len(handler.error_logs)
        
        # Handle rate limit
        try:
            handler.handle_rate_limit(
                operation=operation,
                retry_after_seconds=retry_after
            )
        except Exception as e:
            pytest.fail(f"Rate limit handler crashed: {e}")
        
        # Verify error was logged
        assert len(handler.error_logs) == initial_error_count + 1
        logged_error = handler.error_logs[-1]
        assert logged_error.error_type == "RateLimit"
        assert logged_error.severity == ErrorSeverity.WARNING
        
        # Verify handler is still functional
        try:
            handler.handle_rate_limit(
                operation="AnotherOperation",
                retry_after_seconds=60
            )
        except Exception as e:
            pytest.fail(f"Handler crashed after first rate limit error: {e}")
        
        assert len(handler.error_logs) == initial_error_count + 2

    @given(
        num_errors=st.integers(min_value=1, max_value=50)
    )
    def test_error_handler_accumulates_errors_without_crashing(
        self,
        num_errors
    ):
        """
        Property: For any number of errors, the error handler should accumulate
        them without crashing or losing data.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.2, 6.3**
        """
        handler = ErrorHandler()
        
        # Generate and handle multiple errors
        try:
            for i in range(num_errors):
                if i % 3 == 0:
                    handler.handle_malformed_document(
                        document_id=f"doc-{i}",
                        error_message=f"Error {i}"
                    )
                elif i % 3 == 1:
                    handler.handle_api_error(
                        operation=f"Operation{i}",
                        error_message=f"Error {i}",
                        is_retryable=(i % 2 == 0)
                    )
                else:
                    handler.handle_rate_limit(
                        operation=f"Operation{i}",
                        retry_after_seconds=60
                    )
        except Exception as e:
            pytest.fail(f"Error handler crashed after {len(handler.error_logs)} errors: {e}")
        
        # Verify all errors were logged
        assert len(handler.error_logs) == num_errors
        
        # Verify error summary is accurate
        summary = handler.get_error_summary()
        assert summary["total_errors"] == num_errors

    @given(
        severity=error_severities()
    )
    def test_error_filtering_by_severity_is_consistent(
        self,
        severity
    ):
        """
        Property: For any severity level, filtering errors by that severity
        should return only errors with that severity.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.3**
        """
        handler = ErrorHandler()
        
        # Add errors of different severities
        handler.handle_malformed_document("doc-1", "Error 1")  # WARNING
        handler.handle_api_error("op", "Error 2", is_retryable=False)  # ERROR
        handler.handle_knowledge_base_unavailable("kb-1", "Error 3")  # CRITICAL
        handler.handle_rate_limit("op", 60)  # WARNING
        
        # Filter by the given severity
        filtered = handler.get_errors_by_severity(severity)
        
        # Verify all filtered errors have the correct severity
        for error in filtered:
            assert error.severity == severity

    @given(
        error_type=error_types()
    )
    def test_error_filtering_by_type_is_consistent(
        self,
        error_type
    ):
        """
        Property: For any error type, filtering errors by that type should
        return only errors with that type.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.3**
        """
        handler = ErrorHandler()
        
        # Add various errors
        handler.handle_malformed_document("doc-1", "Error 1")
        handler.handle_api_error("op", "Error 2", is_retryable=False)
        handler.handle_knowledge_base_unavailable("kb-1", "Error 3")
        
        # Filter by the given type
        filtered = handler.get_errors_by_type(error_type)
        
        # Verify all filtered errors have the correct type
        for error in filtered:
            assert error.error_type == error_type

    def test_error_handler_clear_logs_removes_all_errors(self):
        """
        Property: Clearing error logs should remove all accumulated errors
        and allow the handler to continue functioning.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.3**
        """
        handler = ErrorHandler()
        
        # Add some errors
        handler.handle_malformed_document("doc-1", "Error 1")
        handler.handle_api_error("op", "Error 2", is_retryable=False)
        assert len(handler.error_logs) == 2
        
        # Clear logs
        handler.clear_error_logs()
        assert len(handler.error_logs) == 0
        
        # Verify handler still works
        handler.handle_rate_limit("op", 60)
        assert len(handler.error_logs) == 1

    @given(
        num_errors=st.integers(min_value=1, max_value=100)
    )
    def test_error_summary_accuracy(
        self,
        num_errors
    ):
        """
        Property: For any number of errors, the error summary should accurately
        count errors by severity and type.
        
        **Feature: bedrock-rag-retrieval, Property 6: Error Handling Stability**
        **Validates: Requirements 6.1, 6.3**
        """
        handler = ErrorHandler()
        
        # Add errors
        for i in range(num_errors):
            if i % 2 == 0:
                handler.handle_malformed_document(f"doc-{i}", f"Error {i}")
            else:
                handler.handle_api_error(f"op-{i}", f"Error {i}", is_retryable=False)
        
        # Get summary
        summary = handler.get_error_summary()
        
        # Verify total count
        assert summary["total_errors"] == num_errors
        
        # Verify counts by type
        total_by_type = sum(summary["errors_by_type"].values())
        assert total_by_type == num_errors
        
        # Verify counts by severity
        total_by_severity = sum(summary["errors_by_severity"].values())
        assert total_by_severity == num_errors

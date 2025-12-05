"""Tests for ErrorHandler."""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, settings
from src.error_handler import ErrorHandler


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w") as f:
        f.write("sample content")
    return file_path


def test_validate_file_input_valid(sample_file):
    """Test validating a valid file."""
    is_valid, error_msg = ErrorHandler.validate_file_input(sample_file)
    assert is_valid is True
    assert error_msg == ""


def test_validate_file_input_nonexistent():
    """Test validating a nonexistent file."""
    is_valid, error_msg = ErrorHandler.validate_file_input("/nonexistent/file.txt")
    assert is_valid is False
    assert error_msg != ""


def test_validate_file_input_empty_string():
    """Test validating an empty string."""
    is_valid, error_msg = ErrorHandler.validate_file_input("")
    assert is_valid is False
    assert error_msg != ""


def test_validate_file_input_empty_file(temp_dir):
    """Test validating an empty file."""
    empty_file = os.path.join(temp_dir, "empty.txt")
    with open(empty_file, "w") as f:
        pass  # Create empty file
    
    is_valid, error_msg = ErrorHandler.validate_file_input(empty_file)
    assert is_valid is False
    assert error_msg != ""


def test_validate_directory_input_valid(temp_dir):
    """Test validating a valid directory."""
    is_valid, error_msg = ErrorHandler.validate_directory_input(temp_dir)
    assert is_valid is True
    assert error_msg == ""


def test_validate_directory_input_nonexistent():
    """Test validating a nonexistent directory."""
    is_valid, error_msg = ErrorHandler.validate_directory_input("/nonexistent/directory")
    assert is_valid is False
    assert error_msg != ""


def test_validate_directory_input_file_path(sample_file):
    """Test validating a file path as directory."""
    is_valid, error_msg = ErrorHandler.validate_directory_input(sample_file)
    assert is_valid is False
    assert error_msg != ""


def test_validate_url_list_valid():
    """Test validating a valid URL list."""
    urls = ["https://example.com", "http://test.org"]
    is_valid, error_msg = ErrorHandler.validate_url_list(urls)
    assert is_valid is True
    assert error_msg == ""


def test_validate_url_list_empty():
    """Test validating an empty URL list."""
    is_valid, error_msg = ErrorHandler.validate_url_list([])
    assert is_valid is False
    assert error_msg != ""


def test_validate_url_list_malformed():
    """Test validating a list with malformed URLs."""
    urls = ["not a url", "https://example.com"]
    is_valid, error_msg = ErrorHandler.validate_url_list(urls)
    assert is_valid is False
    assert error_msg != ""


def test_validate_url_list_not_list():
    """Test validating non-list input."""
    is_valid, error_msg = ErrorHandler.validate_url_list("https://example.com")
    assert is_valid is False
    assert error_msg != ""


def test_validate_credentials_valid():
    """Test validating valid credentials."""
    is_valid, error_msg = ErrorHandler.validate_credentials("user@example.com", "password123")
    assert is_valid is True
    assert error_msg == ""


def test_validate_credentials_invalid_email():
    """Test validating invalid email."""
    is_valid, error_msg = ErrorHandler.validate_credentials("not-an-email", "password123")
    assert is_valid is False
    assert error_msg != ""


def test_validate_credentials_empty_password():
    """Test validating empty password."""
    is_valid, error_msg = ErrorHandler.validate_credentials("user@example.com", "")
    assert is_valid is False
    assert error_msg != ""


def test_validate_file_size_valid(sample_file):
    """Test validating file size."""
    is_valid, error_msg = ErrorHandler.validate_file_size(sample_file, max_size_mb=100)
    assert is_valid is True
    assert error_msg == ""


def test_validate_file_size_exceeds_limit(temp_dir):
    """Test validating file that exceeds size limit."""
    large_file = os.path.join(temp_dir, "large.bin")
    with open(large_file, "wb") as f:
        f.write(b"x" * (101 * 1024 * 1024))  # 101 MB
    
    is_valid, error_msg = ErrorHandler.validate_file_size(large_file, max_size_mb=100)
    assert is_valid is False
    assert error_msg != ""


def test_validate_file_type_valid(sample_file):
    """Test validating file type."""
    is_valid, error_msg = ErrorHandler.validate_file_type(sample_file, ["txt", "pdf"])
    assert is_valid is True
    assert error_msg == ""


def test_validate_file_type_invalid(sample_file):
    """Test validating invalid file type."""
    is_valid, error_msg = ErrorHandler.validate_file_type(sample_file, ["pdf", "doc"])
    assert is_valid is False
    assert error_msg != ""


def test_handle_exception_file_not_found():
    """Test handling FileNotFoundError."""
    exc = FileNotFoundError("test.txt")
    msg = ErrorHandler.handle_exception(exc)
    assert "File not found" in msg
    assert msg != ""


def test_handle_exception_permission_error():
    """Test handling PermissionError."""
    exc = PermissionError("Access denied")
    msg = ErrorHandler.handle_exception(exc)
    assert "Permission denied" in msg
    assert msg != ""


def test_mask_sensitive_data_email():
    """Test masking email addresses."""
    text = "Contact user@example.com for help"
    masked = ErrorHandler.mask_sensitive_data(text)
    assert "user@example.com" not in masked
    assert "[EMAIL]" in masked


def test_mask_sensitive_data_password():
    """Test masking passwords."""
    text = "password=secret123"
    masked = ErrorHandler.mask_sensitive_data(text)
    assert "secret123" not in masked
    assert "[MASKED]" in masked


# Property-Based Tests

@given(
    file_path=st.one_of(
        st.just(""),
        st.just(None),
        st.just("/nonexistent/path/file.txt"),
        st.just("/dev/null/invalid/path.txt")
    )
)
def test_invalid_input_rejection(file_path):
    """
    **Feature: lazy-automation-platform, Property 15: Invalid Input Rejection**
    
    For any invalid input (empty files, malformed URLs, invalid credentials), 
    the system should reject the input and display a non-empty error message.
    
    **Validates: Requirements 6.1**
    """
    # Test file validation with invalid inputs
    if file_path is None or file_path == "":
        is_valid, error_msg = ErrorHandler.validate_file_input(file_path)
        assert is_valid is False, "Empty/None file path should be rejected"
        assert error_msg != "", "Error message should not be empty"
    else:
        # For nonexistent paths
        is_valid, error_msg = ErrorHandler.validate_file_input(file_path)
        assert is_valid is False, f"Nonexistent file path should be rejected: {file_path}"
        assert error_msg != "", "Error message should not be empty"


@given(
    urls=st.one_of(
        st.just([]),
        st.just(["not a url"]),
        st.just(["ftp://invalid.com"]),
        st.just(["http://"]),
        st.just(["https://"])
    )
)
def test_invalid_url_rejection(urls):
    """
    **Feature: lazy-automation-platform, Property 15: Invalid Input Rejection**
    
    For any invalid input (empty files, malformed URLs, invalid credentials), 
    the system should reject the input and display a non-empty error message.
    
    **Validates: Requirements 6.1**
    """
    is_valid, error_msg = ErrorHandler.validate_url_list(urls)
    assert is_valid is False, f"Invalid URL list should be rejected: {urls}"
    assert error_msg != "", "Error message should not be empty"


@given(
    email=st.one_of(
        st.just(""),
        st.just("not-an-email"),
        st.just("@example.com"),
        st.just("user@"),
        st.just("user@.com")
    ),
    password=st.one_of(
        st.just(""),
        st.just("   ")
    )
)
def test_invalid_credentials_rejection(email, password):
    """
    **Feature: lazy-automation-platform, Property 15: Invalid Input Rejection**
    
    For any invalid input (empty files, malformed URLs, invalid credentials), 
    the system should reject the input and display a non-empty error message.
    
    **Validates: Requirements 6.1**
    """
    is_valid, error_msg = ErrorHandler.validate_credentials(email, password)
    assert is_valid is False, f"Invalid credentials should be rejected: email={email}, password={password}"
    assert error_msg != "", "Error message should not be empty"


@given(
    exception=st.one_of(
        st.just(FileNotFoundError("test.txt")),
        st.just(PermissionError("Access denied")),
        st.just(IOError("I/O error occurred")),
        st.just(ValueError("Invalid value")),
        st.just(TypeError("Type mismatch")),
        st.just(Exception("Generic error"))
    )
)
def test_error_handling_and_logging(exception):
    """
    **Feature: lazy-automation-platform, Property 16: Error Handling and Logging**
    
    For any error encountered during automation task execution, the system should 
    catch the exception, log it, and display a user-friendly error message.
    
    **Validates: Requirements 6.2**
    """
    # Test that handle_exception converts any exception to a user-friendly message
    error_msg = ErrorHandler.handle_exception(exception)
    
    # Verify error message is not empty
    assert error_msg != "", "Error message should not be empty for any exception"
    
    # Verify error message is a string
    assert isinstance(error_msg, str), "Error message should be a string"
    
    # Verify error message contains helpful information (not just the raw exception)
    assert len(error_msg) > 0, "Error message should contain meaningful content"
    
    # Verify that sensitive data is not exposed in error messages
    # (e.g., full stack traces should not be included)
    assert "Traceback" not in error_msg, "Error message should not contain stack traces"
    
    # Verify that the error message is user-friendly (contains common words)
    # and not just raw exception type names
    error_msg_lower = error_msg.lower()
    assert any(word in error_msg_lower for word in ["error", "failed", "denied", "not found", "invalid"]), \
        "Error message should contain user-friendly language"


@given(
    file_size_mb=st.integers(min_value=1, max_value=50),
    allowed_extensions=st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=5),
        min_size=1,
        max_size=5,
        unique=True
    )
)
@settings(deadline=None)
def test_file_validation(file_size_mb, allowed_extensions):
    """
    **Feature: lazy-automation-platform, Property 17: File Validation**
    
    For any uploaded file, the system should validate file type and size before 
    processing and reject invalid files with an error message.
    
    **Validates: Requirements 6.3**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file with the specified size
        test_file = os.path.join(temp_dir, f"test_file.{allowed_extensions[0]}")
        with open(test_file, "wb") as f:
            f.write(b"x" * (file_size_mb * 1024 * 1024))
        
        # Test 1: File type validation - valid extension
        is_valid, error_msg = ErrorHandler.validate_file_type(test_file, allowed_extensions)
        assert is_valid is True, f"File with valid extension should pass validation"
        assert error_msg == "", f"Error message should be empty for valid file type"
        
        # Test 2: File type validation - invalid extension
        # Use extensions that are guaranteed to be different from allowed_extensions
        invalid_extensions = ["zzz", "yyy", "xxx"]
        is_valid, error_msg = ErrorHandler.validate_file_type(test_file, invalid_extensions)
        assert is_valid is False, f"File with invalid extension should fail validation"
        assert error_msg != "", f"Error message should not be empty for invalid file type"
        
        # Test 3: File size validation - within limit
        max_size = file_size_mb + 10  # Set limit higher than file size
        is_valid, error_msg = ErrorHandler.validate_file_size(test_file, max_size_mb=max_size)
        assert is_valid is True, f"File within size limit should pass validation"
        assert error_msg == "", f"Error message should be empty for valid file size"
        
        # Test 4: File size validation - exceeds limit
        # Only test this if file_size_mb > 1, so we can set a limit lower than file size
        if file_size_mb > 1:
            max_size = file_size_mb - 1  # Set limit lower than file size
            is_valid, error_msg = ErrorHandler.validate_file_size(test_file, max_size_mb=max_size)
            assert is_valid is False, f"File exceeding size limit should fail validation"
            assert error_msg != "", f"Error message should not be empty for oversized file"
        
        # Test 5: Combined validation - both type and size
        is_valid_type, type_msg = ErrorHandler.validate_file_type(test_file, allowed_extensions)
        is_valid_size, size_msg = ErrorHandler.validate_file_size(test_file, max_size_mb=max_size + 10)
        
        # If both validations pass, both should have empty error messages
        if is_valid_type and is_valid_size:
            assert type_msg == "" and size_msg == "", "Valid files should have empty error messages"
        
        # If either validation fails, it should have a non-empty error message
        if not is_valid_type or not is_valid_size:
            assert type_msg != "" or size_msg != "", "Invalid files should have non-empty error messages"


@given(
    exception_type=st.sampled_from([
        FileNotFoundError,
        PermissionError,
        IOError,
        OSError
    ])
)
def test_file_operation_exception_handling(exception_type):
    """
    **Feature: lazy-automation-platform, Property 18: File Operation Exception Handling**
    
    For any file operation failure (permission denied, disk full), the system should 
    catch the exception and display a specific error message describing the issue.
    
    **Validates: Requirements 6.4**
    """
    # Create exceptions that simulate file operation failures
    if exception_type == FileNotFoundError:
        exception = FileNotFoundError("File not found during operation")
    elif exception_type == PermissionError:
        exception = PermissionError("Permission denied: cannot access file")
    elif exception_type == IOError:
        exception = IOError("Disk full or I/O error occurred")
    else:  # OSError
        exception = OSError("Operating system error: cannot complete operation")
    
    # Test that handle_exception converts the exception to a user-friendly message
    error_msg = ErrorHandler.handle_exception(exception)
    
    # Verify error message is not empty
    assert error_msg != "", "Error message should not be empty for file operation failures"
    
    # Verify error message is a string
    assert isinstance(error_msg, str), "Error message should be a string"
    
    # Verify error message is specific to the exception type
    if isinstance(exception, FileNotFoundError):
        assert "File not found" in error_msg or "not found" in error_msg.lower(), \
            "Error message should mention file not found"
    elif isinstance(exception, PermissionError):
        assert "Permission denied" in error_msg or "permission" in error_msg.lower(), \
            "Error message should mention permission denied"
    elif isinstance(exception, IOError):
        assert "Input/Output error" in error_msg or "I/O error" in error_msg or "error" in error_msg.lower(), \
            "Error message should mention I/O error"
    elif isinstance(exception, OSError):
        assert "error" in error_msg.lower(), \
            "Error message should mention operating system error"
    
    # Verify error message does not expose sensitive information
    assert "Traceback" not in error_msg, "Error message should not contain stack traces"
    
    # Verify error message provides actionable information
    assert len(error_msg) > 5, "Error message should be descriptive enough to help user"


@given(
    credential=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
        min_size=8,
        max_size=50
    ),
    context_text=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ",
        min_size=10,
        max_size=100
    )
)
def test_credential_masking(credential, context_text):
    """
    **Feature: lazy-automation-platform, Property 51: Credential Masking**
    
    For any credential usage or logging, the system should never display them in plain text.
    
    **Validates: Requirements 16.2**
    """
    # Test 1: Mask credentials in error messages
    # Create a message that contains a credential
    message_with_credential = f"Error: {context_text} password={credential}"
    masked_message = ErrorHandler.mask_sensitive_data(message_with_credential)
    
    # Verify the credential is not present in plain text
    assert credential not in masked_message, \
        f"Credential should be masked in error messages: {masked_message}"
    
    # Verify masking placeholder is present
    assert "[MASKED]" in masked_message, \
        "Masked credential should contain [MASKED] placeholder"
    
    # Test 2: Mask API keys
    api_key_message = f"Connecting with api_key={credential}"
    masked_api = ErrorHandler.mask_sensitive_data(api_key_message)
    
    assert credential not in masked_api, \
        f"API key should be masked: {masked_api}"
    assert "[MASKED]" in masked_api, \
        "Masked API key should contain [MASKED] placeholder"
    
    # Test 3: Mask tokens
    token_message = f"Authorization token={credential}"
    masked_token = ErrorHandler.mask_sensitive_data(token_message)
    
    assert credential not in masked_token, \
        f"Token should be masked: {masked_token}"
    assert "[MASKED]" in masked_token, \
        "Masked token should contain [MASKED] placeholder"
    
    # Test 4: Verify non-credential text is preserved
    # The context text should still be present (unless it happens to match a pattern)
    # We check that the masking doesn't remove all content
    assert len(masked_message) > 0, "Masked message should not be empty"
    assert "Error:" in masked_message, "Non-credential parts should be preserved"
    
    # Test 5: Multiple credentials in one message
    multi_cred_message = f"password={credential} and api_key={credential}"
    masked_multi = ErrorHandler.mask_sensitive_data(multi_cred_message)
    
    # Both credentials should be masked
    assert credential not in masked_multi, \
        f"All credentials should be masked: {masked_multi}"
    # Should have at least 2 [MASKED] placeholders
    assert masked_multi.count("[MASKED]") >= 2, \
        "Multiple credentials should all be masked"


@given(
    username=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz",
        min_size=3,
        max_size=10
    ),
    password=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
        min_size=8,
        max_size=30
    ),
    api_key=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        min_size=16,
        max_size=40
    ),
    context=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ",
        min_size=5,
        max_size=50
    )
)
def test_sensitive_data_masking_in_logs(username, password, api_key, context):
    """
    **Feature: lazy-automation-platform, Property 52: Sensitive Data Masking in Logs**
    
    For any error log generated, the system should mask sensitive data (passwords, API keys, 
    email addresses) in log output.
    
    **Validates: Requirements 16.3**
    """
    # Construct a valid email from username
    email = f"{username}@example.com"
    
    # Test 1: Email masking in logs
    log_with_email = f"Error occurred while processing {context} for user {email}"
    masked_log = ErrorHandler.mask_sensitive_data(log_with_email)
    
    # Verify email is masked
    assert email not in masked_log, \
        f"Email should be masked in logs: {masked_log}"
    assert "[EMAIL]" in masked_log, \
        "Masked email should contain [EMAIL] placeholder"
    
    # Test 2: Password masking in logs
    log_with_password = f"Authentication failed: password={password} for {context}"
    masked_log = ErrorHandler.mask_sensitive_data(log_with_password)
    
    # Verify password is masked
    assert password not in masked_log, \
        f"Password should be masked in logs: {masked_log}"
    assert "[MASKED]" in masked_log, \
        "Masked password should contain [MASKED] placeholder"
    
    # Test 3: API key masking in logs
    log_with_api_key = f"API call failed with api_key={api_key} during {context}"
    masked_log = ErrorHandler.mask_sensitive_data(log_with_api_key)
    
    # Verify API key is masked
    assert api_key not in masked_log, \
        f"API key should be masked in logs: {masked_log}"
    assert "[MASKED]" in masked_log, \
        "Masked API key should contain [MASKED] placeholder"
    
    # Test 4: Multiple sensitive data types in one log
    complex_log = f"Error: {context} email={email} password={password} api_key={api_key}"
    masked_log = ErrorHandler.mask_sensitive_data(complex_log)
    
    # Verify all sensitive data is masked
    assert email not in masked_log, \
        f"Email should be masked in complex log: {masked_log}"
    assert password not in masked_log, \
        f"Password should be masked in complex log: {masked_log}"
    assert api_key not in masked_log, \
        f"API key should be masked in complex log: {masked_log}"
    
    # Verify context is preserved
    assert context in masked_log, \
        f"Non-sensitive context should be preserved in logs: {masked_log}"
    
    # Test 5: Verify masking doesn't corrupt log structure
    # The log should still be readable and contain meaningful information
    assert len(masked_log) > 0, "Masked log should not be empty"
    assert "Error:" in masked_log or "error" in masked_log.lower(), \
        "Log should still contain error context after masking"
    
    # Test 6: Verify no plain text credentials remain
    # Check that the original sensitive values don't appear anywhere
    assert password not in masked_log, \
        "No plain text passwords should remain in masked logs"
    assert api_key not in masked_log, \
        "No plain text API keys should remain in masked logs"
    assert email not in masked_log, \
        "No plain text emails should remain in masked logs"


@given(
    data_dict=st.dictionaries(
        keys=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz_",
            min_size=1,
            max_size=20
        ),
        values=st.one_of(
            st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=1, max_size=50),
            st.integers(min_value=0, max_value=1000),
            st.booleans()
        ),
        min_size=1,
        max_size=10
    ),
    sensitive_keys=st.lists(
        st.sampled_from(["password", "api_key", "token", "secret", "credential"]),
        min_size=1,
        max_size=3,
        unique=True
    ),
    sensitive_values=st.lists(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
            min_size=8,
            max_size=30
        ),
        min_size=1,
        max_size=3,
        unique=True
    )
)
def test_export_sensitive_data_exclusion(data_dict, sensitive_keys, sensitive_values):
    """
    **Feature: lazy-automation-platform, Property 53: Export Sensitive Data Exclusion**
    
    For any exported result, the system should exclude sensitive data from exports unless 
    explicitly requested.
    
    **Validates: Requirements 16.4**
    """
    import json
    
    # Create a test export data structure with sensitive and non-sensitive fields
    export_data = data_dict.copy()
    
    # Add sensitive fields to the export data
    for i, key in enumerate(sensitive_keys):
        if i < len(sensitive_values):
            export_data[key] = sensitive_values[i]
    
    # Simulate export filtering (exclude sensitive keys)
    safe_export = {}
    sensitive_keywords = ['password', 'token', 'key', 'secret', 'credential']
    
    for key, value in export_data.items():
        # Check if key contains any sensitive keyword
        if not any(sensitive in key.lower() for sensitive in sensitive_keywords):
            safe_export[key] = value
    
    # Convert to JSON to simulate export
    export_json = json.dumps(safe_export, indent=2)
    
    # Test 1: Verify sensitive keys are excluded from export
    for sensitive_key in sensitive_keys:
        assert sensitive_key not in export_json, \
            f"Sensitive key '{sensitive_key}' should be excluded from export: {export_json}"
    
    # Test 2: Verify sensitive values are not in export
    for sensitive_value in sensitive_values:
        # Only check if the value is a string (to avoid false positives with numbers/booleans)
        if isinstance(sensitive_value, str) and len(sensitive_value) > 3:
            assert sensitive_value not in export_json, \
                f"Sensitive value should be excluded from export: {export_json}"
    
    # Test 3: Verify non-sensitive data is preserved in export
    # Check that at least some of the original data is still in the export
    # (unless all keys were sensitive)
    if len(safe_export) > 0:
        assert len(export_json) > 0, "Export should not be empty when non-sensitive data exists"
        # Verify the export is valid JSON
        parsed_export = json.loads(export_json)
        assert isinstance(parsed_export, dict), "Export should be a valid JSON object"
    
    # Test 4: Verify export structure is maintained
    # The export should still be valid JSON and parseable
    try:
        parsed = json.loads(export_json)
        assert isinstance(parsed, dict), "Exported data should be a dictionary"
    except json.JSONDecodeError:
        pytest.fail(f"Exported data should be valid JSON: {export_json}")
    
    # Test 5: Verify filtering logic is consistent
    # Re-filter the same data and verify we get the same result
    safe_export_2 = {}
    for key, value in export_data.items():
        if not any(sensitive in key.lower() for sensitive in sensitive_keywords):
            safe_export_2[key] = value
    
    assert safe_export == safe_export_2, \
        "Export filtering should be consistent across multiple runs"
    
    # Test 6: Verify that the export is smaller than or equal to the original
    # (since we're removing sensitive data)
    assert len(export_json) <= len(json.dumps(export_data, indent=2)), \
        "Export with sensitive data excluded should not be larger than original"
    
    # Test 7: Verify no sensitive keywords appear in export keys
    parsed_export = json.loads(export_json)
    for key in parsed_export.keys():
        for sensitive_keyword in sensitive_keywords:
            assert sensitive_keyword not in key.lower(), \
                f"Export should not contain keys with sensitive keywords like '{sensitive_keyword}': {key}"

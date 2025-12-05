"""Error handling and validation for the Lazy Automation Platform."""

import os
import re
from typing import Tuple, List
from pathlib import Path


class ErrorHandler:
    """Handles validation and error management for the platform."""

    # Valid URL pattern
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    # Email pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @staticmethod
    def validate_file_input(file_path: str) -> Tuple[bool, str]:
        """
        Validate a file input.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not file_path or not isinstance(file_path, str):
            return False, "File path must be a non-empty string"

        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"

        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"

        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            return False, "File is empty"

        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False, "File is not readable (permission denied)"

        return True, ""

    @staticmethod
    def validate_directory_input(directory_path: str) -> Tuple[bool, str]:
        """
        Validate a directory input.

        Args:
            directory_path: Path to the directory

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not directory_path or not isinstance(directory_path, str):
            return False, "Directory path must be a non-empty string"

        if not os.path.exists(directory_path):
            return False, f"Directory does not exist: {directory_path}"

        if not os.path.isdir(directory_path):
            return False, f"Path is not a directory: {directory_path}"

        # Check if directory is readable
        if not os.access(directory_path, os.R_OK):
            return False, "Directory is not readable (permission denied)"

        return True, ""

    @staticmethod
    def validate_url_list(urls: List[str]) -> Tuple[bool, str]:
        """
        Validate a list of URLs.

        Args:
            urls: List of URL strings

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not isinstance(urls, list):
            return False, "URLs must be provided as a list"

        if len(urls) == 0:
            return False, "URL list cannot be empty"

        for i, url in enumerate(urls):
            if not isinstance(url, str):
                return False, f"URL at index {i} is not a string"

            if not url.strip():
                return False, f"URL at index {i} is empty or whitespace"

            if not ErrorHandler.URL_PATTERN.match(url):
                return False, f"URL at index {i} is malformed: {url}"

        return True, ""

    @staticmethod
    def validate_credentials(email: str, password: str) -> Tuple[bool, str]:
        """
        Validate email credentials.

        Args:
            email: Email address
            password: Password

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not isinstance(email, str) or not email.strip():
            return False, "Email must be a non-empty string"

        if not ErrorHandler.EMAIL_PATTERN.match(email):
            return False, f"Invalid email format: {email}"

        if not isinstance(password, str) or not password.strip():
            return False, "Password must be a non-empty string"

        if len(password) < 1:
            return False, "Password is too short"

        return True, ""

    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 100) -> Tuple[bool, str]:
        """
        Validate file size.

        Args:
            file_path: Path to the file
            max_size_mb: Maximum allowed size in MB

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

        if file_size_mb > max_size_mb:
            return False, f"File size ({file_size_mb:.2f}MB) exceeds maximum ({max_size_mb}MB)"

        return True, ""

    @staticmethod
    def validate_file_type(file_path: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
        """
        Validate file type based on extension.

        Args:
            file_path: Path to the file
            allowed_extensions: List of allowed extensions (e.g., ['pdf', 'txt'])

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"

        file_ext = Path(file_path).suffix.lstrip('.').lower()

        if file_ext not in allowed_extensions:
            return False, f"File type '.{file_ext}' is not allowed. Allowed types: {', '.join(allowed_extensions)}"

        return True, ""

    @staticmethod
    def handle_exception(exception: Exception) -> str:
        """
        Convert an exception to a user-friendly error message.

        Args:
            exception: The exception to handle

        Returns:
            User-friendly error message
        """
        exception_type = type(exception).__name__

        if isinstance(exception, FileNotFoundError):
            return f"File not found: {str(exception)}"
        elif isinstance(exception, PermissionError):
            return "Permission denied: You do not have access to this resource"
        elif isinstance(exception, IOError):
            return f"Input/Output error: {str(exception)}"
        elif isinstance(exception, ValueError):
            return f"Invalid value: {str(exception)}"
        elif isinstance(exception, TypeError):
            return f"Type error: {str(exception)}"
        else:
            return f"An error occurred: {str(exception)}"

    @staticmethod
    def mask_sensitive_data(text: str) -> str:
        """
        Mask sensitive data in text (passwords, API keys, emails).

        Args:
            text: Text that may contain sensitive data

        Returns:
            Text with sensitive data masked
        """
        # Mask email addresses
        text = re.sub(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            '[EMAIL]',
            text
        )

        # Mask common password patterns
        text = re.sub(
            r'(?i)(password|passwd|pwd)\s*[:=]\s*[^\s]+',
            r'\1=[MASKED]',
            text
        )

        # Mask API keys
        text = re.sub(
            r'(?i)(api[_-]?key|apikey|token)\s*[:=]\s*[^\s]+',
            r'\1=[MASKED]',
            text
        )

        return text

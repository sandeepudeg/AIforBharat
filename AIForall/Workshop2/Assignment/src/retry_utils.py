"""Retry logic with exponential backoff for Bedrock RAG Retrieval System"""

import time
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps
from botocore.exceptions import ClientError


class RetryConfig:
    """Configuration for retry behavior"""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts (default: 3)
            initial_delay: Initial delay in seconds (default: 1.0)
            max_delay: Maximum delay in seconds (default: 60.0)
            exponential_base: Base for exponential backoff (default: 2.0)
            jitter: Whether to add random jitter to delays (default: True)
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            import random
            # Add random jitter: ±10% of the delay
            jitter_amount = delay * 0.1
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure non-negative

        return delay


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable, False otherwise
    """
    if isinstance(error, ClientError):
        error_code = error.response.get('Error', {}).get('Code', '')
        
        # Retryable error codes from AWS
        retryable_codes = {
            'ThrottlingException',
            'RequestLimitExceeded',
            'ServiceUnavailable',
            'InternalServerError',
            'RequestTimeout',
            'ConnectionError',
            'ProvisionedThroughputExceededException',
            'LimitExceededException',
            'TooManyRequestsException',
        }
        
        return error_code in retryable_codes
    
    # Retry on connection errors and timeouts
    return isinstance(error, (ConnectionError, TimeoutError))


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        config: RetryConfig instance (uses defaults if not provided)
        retryable_exceptions: Tuple of exception types to retry on
                             (defaults to ClientError, ConnectionError, TimeoutError)
        logger: Logger instance for logging retry attempts

    Returns:
        Decorator function

    Example:
        @retry_with_backoff()
        def my_api_call():
            # API call that might fail
            pass

        @retry_with_backoff(
            config=RetryConfig(max_attempts=5, initial_delay=2.0),
            retryable_exceptions=(ClientError, ValueError)
        )
        def another_api_call():
            # Another API call
            pass
    """
    if config is None:
        config = RetryConfig()

    if retryable_exceptions is None:
        retryable_exceptions = (ClientError, ConnectionError, TimeoutError)

    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    # For ClientError, check if it's actually retryable
                    if isinstance(e, ClientError) and not is_retryable_error(e):
                        logger.error(
                            f"Non-retryable error in {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    # If this is the last attempt, raise the exception
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Max retry attempts ({config.max_attempts}) exceeded "
                            f"for {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    # Calculate delay and log retry attempt
                    delay = config.get_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts} "
                        f"for {func.__name__} after {delay:.2f}s delay. "
                        f"Error: {str(e)}"
                    )
                    
                    # Sleep before retrying
                    time.sleep(delay)
            
            # This should not be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    
    return decorator


def retry_on_rate_limit(
    config: Optional[RetryConfig] = None,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    Decorator specifically for handling rate limit errors.

    This decorator detects rate limit errors and retries with exponential backoff.
    It respects the 'Retry-After' header if present in the error response.

    Args:
        config: RetryConfig instance (uses defaults if not provided)
        logger: Logger instance for logging retry attempts

    Returns:
        Decorator function

    Example:
        @retry_on_rate_limit()
        def api_call_that_might_be_rate_limited():
            # API call
            pass
    """
    if config is None:
        config = RetryConfig(max_attempts=5, initial_delay=1.0)

    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    
                    # Check if this is a rate limit error
                    rate_limit_codes = {
                        'ThrottlingException',
                        'RequestLimitExceeded',
                        'TooManyRequestsException',
                        'ProvisionedThroughputExceededException',
                    }
                    
                    if error_code not in rate_limit_codes:
                        logger.error(
                            f"Non-rate-limit error in {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    # If this is the last attempt, raise the exception
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Max retry attempts ({config.max_attempts}) exceeded "
                            f"for {func.__name__} due to rate limiting: {str(e)}"
                        )
                        raise
                    
                    # Check for Retry-After header
                    retry_after = e.response.get('ResponseMetadata', {}).get(
                        'HTTPHeaders', {}
                    ).get('retry-after')
                    
                    if retry_after:
                        try:
                            delay = float(retry_after)
                        except (ValueError, TypeError):
                            delay = config.get_delay(attempt)
                    else:
                        delay = config.get_delay(attempt)
                    
                    logger.warning(
                        f"Rate limit detected in {func.__name__}. "
                        f"Retry attempt {attempt + 1}/{config.max_attempts} "
                        f"after {delay:.2f}s delay."
                    )
                    
                    time.sleep(delay)
                    last_exception = e
                except (ConnectionError, TimeoutError) as e:
                    # Also retry on connection errors
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Max retry attempts ({config.max_attempts}) exceeded "
                            f"for {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    delay = config.get_delay(attempt)
                    logger.warning(
                        f"Connection error in {func.__name__}. "
                        f"Retry attempt {attempt + 1}/{config.max_attempts} "
                        f"after {delay:.2f}s delay. Error: {str(e)}"
                    )
                    
                    time.sleep(delay)
                    last_exception = e
            
            # This should not be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator

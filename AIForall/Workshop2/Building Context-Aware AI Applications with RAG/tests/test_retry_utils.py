"""Tests for Retry Utilities"""

import pytest
import time
import logging
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from src.retry_utils import (
    RetryConfig,
    is_retryable_error,
    retry_with_backoff,
    retry_on_rate_limit
)


class TestRetryConfig:
    """Tests for RetryConfig class"""

    def test_retry_config_defaults(self):
        """Test RetryConfig with default values"""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_retry_config_custom_values(self):
        """Test RetryConfig with custom values"""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=1.5,
            jitter=False
        )

        assert config.max_attempts == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 1.5
        assert config.jitter is False

    def test_retry_config_get_delay_exponential(self):
        """Test exponential delay calculation"""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            jitter=False
        )

        # Attempt 0: 1.0 * 2^0 = 1.0
        assert config.get_delay(0) == 1.0
        # Attempt 1: 1.0 * 2^1 = 2.0
        assert config.get_delay(1) == 2.0
        # Attempt 2: 1.0 * 2^2 = 4.0
        assert config.get_delay(2) == 4.0

    def test_retry_config_get_delay_max_delay_cap(self):
        """Test that delay is capped at max_delay"""
        config = RetryConfig(
            initial_delay=1.0,
            max_delay=10.0,
            exponential_base=2.0,
            jitter=False
        )

        # Attempt 4: 1.0 * 2^4 = 16.0, but capped at 10.0
        assert config.get_delay(4) == 10.0

    def test_retry_config_get_delay_with_jitter(self):
        """Test delay calculation with jitter"""
        config = RetryConfig(
            initial_delay=10.0,
            exponential_base=1.0,
            jitter=True
        )

        # With jitter, delay should be around 10.0 ±10%
        delays = [config.get_delay(0) for _ in range(10)]
        
        for delay in delays:
            # Should be between 9.0 and 11.0 (±10% of 10.0)
            assert 8.0 <= delay <= 12.0

    def test_retry_config_get_delay_jitter_non_negative(self):
        """Test that jitter doesn't produce negative delays"""
        config = RetryConfig(
            initial_delay=0.1,
            exponential_base=1.0,
            jitter=True
        )

        # Run multiple times to ensure jitter never produces negative
        for _ in range(20):
            delay = config.get_delay(0)
            assert delay >= 0


class TestIsRetryableError:
    """Tests for is_retryable_error function"""

    def test_is_retryable_throttling_exception(self):
        """Test that ThrottlingException is retryable"""
        error = ClientError(
            {'Error': {'Code': 'ThrottlingException', 'Message': 'Throttled'}},
            'TestOperation'
        )
        assert is_retryable_error(error) is True

    def test_is_retryable_service_unavailable(self):
        """Test that ServiceUnavailable is retryable"""
        error = ClientError(
            {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Service down'}},
            'TestOperation'
        )
        assert is_retryable_error(error) is True

    def test_is_retryable_internal_server_error(self):
        """Test that InternalServerError is retryable"""
        error = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'Server error'}},
            'TestOperation'
        )
        assert is_retryable_error(error) is True

    def test_is_retryable_request_timeout(self):
        """Test that RequestTimeout is retryable"""
        error = ClientError(
            {'Error': {'Code': 'RequestTimeout', 'Message': 'Timeout'}},
            'TestOperation'
        )
        assert is_retryable_error(error) is True

    def test_is_not_retryable_access_denied(self):
        """Test that AccessDenied is not retryable"""
        error = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'TestOperation'
        )
        assert is_retryable_error(error) is False

    def test_is_not_retryable_validation_error(self):
        """Test that ValidationException is not retryable"""
        error = ClientError(
            {'Error': {'Code': 'ValidationException', 'Message': 'Invalid input'}},
            'TestOperation'
        )
        assert is_retryable_error(error) is False

    def test_is_retryable_connection_error(self):
        """Test that ConnectionError is retryable"""
        error = ConnectionError("Connection failed")
        assert is_retryable_error(error) is True

    def test_is_retryable_timeout_error(self):
        """Test that TimeoutError is retryable"""
        error = TimeoutError("Request timed out")
        assert is_retryable_error(error) is True

    def test_is_not_retryable_value_error(self):
        """Test that ValueError is not retryable"""
        error = ValueError("Invalid value")
        assert is_retryable_error(error) is False


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator"""

    def test_retry_succeeds_on_first_attempt(self):
        """Test function succeeds on first attempt"""
        mock_func = Mock(return_value="success")
        
        @retry_with_backoff()
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_succeeds_after_retries(self):
        """Test function succeeds after retries"""
        mock_func = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Down'}},
                    'TestOp'
                ),
                ClientError(
                    {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Down'}},
                    'TestOp'
                ),
                "success"
            ]
        )
        
        @retry_with_backoff(config=RetryConfig(max_attempts=3, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_fails_after_max_attempts(self):
        """Test function fails after max attempts"""
        mock_func = Mock(
            side_effect=ClientError(
                {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Down'}},
                'TestOp'
            )
        )
        
        @retry_with_backoff(config=RetryConfig(max_attempts=2, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        with pytest.raises(ClientError):
            test_func()
        
        assert mock_func.call_count == 2

    def test_retry_non_retryable_error_fails_immediately(self):
        """Test non-retryable error fails immediately"""
        mock_func = Mock(
            side_effect=ClientError(
                {'Error': {'Code': 'AccessDenied', 'Message': 'Denied'}},
                'TestOp'
            )
        )
        
        @retry_with_backoff(config=RetryConfig(max_attempts=3, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        with pytest.raises(ClientError):
            test_func()
        
        # Should fail immediately without retries
        assert mock_func.call_count == 1

    def test_retry_with_custom_retryable_exceptions(self):
        """Test retry with custom retryable exceptions"""
        mock_func = Mock(
            side_effect=[
                ValueError("Custom error"),
                ValueError("Custom error"),
                "success"
            ]
        )
        
        @retry_with_backoff(
            config=RetryConfig(max_attempts=3, initial_delay=0.01),
            retryable_exceptions=(ValueError,)
        )
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 3

    def test_retry_logs_attempts(self):
        """Test that retry attempts are logged"""
        mock_func = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Down'}},
                    'TestOp'
                ),
                "success"
            ]
        )
        
        mock_logger = Mock()
        
        @retry_with_backoff(
            config=RetryConfig(max_attempts=2, initial_delay=0.01),
            logger=mock_logger
        )
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        # Should log the retry attempt
        assert mock_logger.warning.called

    def test_retry_preserves_function_metadata(self):
        """Test that decorator preserves function metadata"""
        @retry_with_backoff()
        def my_function():
            """My function docstring"""
            pass
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring"

    def test_retry_with_function_arguments(self):
        """Test retry with function arguments"""
        mock_func = Mock(return_value="success")
        
        @retry_with_backoff()
        def test_func(a, b, c=None):
            return mock_func(a, b, c)
        
        result = test_func(1, 2, c=3)
        
        assert result == "success"
        mock_func.assert_called_once_with(1, 2, 3)

    def test_retry_respects_max_delay(self):
        """Test that retry respects max delay"""
        mock_func = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Down'}},
                    'TestOp'
                ),
                ClientError(
                    {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Down'}},
                    'TestOp'
                ),
                "success"
            ]
        )
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=2.0,
            exponential_base=10.0,  # Would create very large delays
            jitter=False
        )
        
        @retry_with_backoff(config=config)
        def test_func():
            return mock_func()
        
        start = time.time()
        result = test_func()
        elapsed = time.time() - start
        
        assert result == "success"
        # Should not exceed max_delay * 2 (for 2 retries)
        assert elapsed < 5.0


class TestRetryOnRateLimit:
    """Tests for retry_on_rate_limit decorator"""

    def test_retry_on_rate_limit_succeeds_on_first_attempt(self):
        """Test function succeeds on first attempt"""
        mock_func = Mock(return_value="success")
        
        @retry_on_rate_limit()
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_rate_limit_throttling_exception(self):
        """Test retry on ThrottlingException"""
        mock_func = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'ThrottlingException', 'Message': 'Throttled'}},
                    'TestOp'
                ),
                "success"
            ]
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=2, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_rate_limit_request_limit_exceeded(self):
        """Test retry on RequestLimitExceeded"""
        mock_func = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'RequestLimitExceeded', 'Message': 'Limit'}},
                    'TestOp'
                ),
                "success"
            ]
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=2, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_rate_limit_non_rate_limit_error_fails(self):
        """Test non-rate-limit error fails immediately"""
        mock_func = Mock(
            side_effect=ClientError(
                {'Error': {'Code': 'AccessDenied', 'Message': 'Denied'}},
                'TestOp'
            )
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=3, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        with pytest.raises(ClientError):
            test_func()
        
        # Should fail immediately without retries
        assert mock_func.call_count == 1

    def test_retry_on_rate_limit_respects_retry_after_header(self):
        """Test that Retry-After header is respected"""
        error_response = {
            'Error': {'Code': 'ThrottlingException', 'Message': 'Throttled'},
            'ResponseMetadata': {
                'HTTPHeaders': {'retry-after': '0.05'}
            }
        }
        
        mock_func = Mock(
            side_effect=[
                ClientError(error_response, 'TestOp'),
                "success"
            ]
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=2, initial_delay=1.0))
        def test_func():
            return mock_func()
        
        start = time.time()
        result = test_func()
        elapsed = time.time() - start
        
        assert result == "success"
        # Should use Retry-After (0.05) instead of initial_delay (1.0)
        assert elapsed < 0.5

    def test_retry_on_rate_limit_connection_error(self):
        """Test retry on ConnectionError"""
        mock_func = Mock(
            side_effect=[
                ConnectionError("Connection failed"),
                "success"
            ]
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=2, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_rate_limit_timeout_error(self):
        """Test retry on TimeoutError"""
        mock_func = Mock(
            side_effect=[
                TimeoutError("Request timed out"),
                "success"
            ]
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=2, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_rate_limit_logs_attempts(self):
        """Test that rate limit retry attempts are logged"""
        mock_func = Mock(
            side_effect=[
                ClientError(
                    {'Error': {'Code': 'ThrottlingException', 'Message': 'Throttled'}},
                    'TestOp'
                ),
                "success"
            ]
        )
        
        mock_logger = Mock()
        
        @retry_on_rate_limit(
            config=RetryConfig(max_attempts=2, initial_delay=0.01),
            logger=mock_logger
        )
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        # Should log the rate limit detection
        assert mock_logger.warning.called

    def test_retry_on_rate_limit_preserves_function_metadata(self):
        """Test that decorator preserves function metadata"""
        @retry_on_rate_limit()
        def my_function():
            """My function docstring"""
            pass
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My function docstring"

    def test_retry_on_rate_limit_with_function_arguments(self):
        """Test retry on rate limit with function arguments"""
        mock_func = Mock(return_value="success")
        
        @retry_on_rate_limit()
        def test_func(a, b, c=None):
            return mock_func(a, b, c)
        
        result = test_func(1, 2, c=3)
        
        assert result == "success"
        mock_func.assert_called_once_with(1, 2, 3)

    def test_retry_on_rate_limit_max_attempts_exceeded(self):
        """Test that max attempts are respected"""
        mock_func = Mock(
            side_effect=ClientError(
                {'Error': {'Code': 'ThrottlingException', 'Message': 'Throttled'}},
                'TestOp'
            )
        )
        
        @retry_on_rate_limit(config=RetryConfig(max_attempts=2, initial_delay=0.01))
        def test_func():
            return mock_func()
        
        with pytest.raises(ClientError):
            test_func()
        
        assert mock_func.call_count == 2

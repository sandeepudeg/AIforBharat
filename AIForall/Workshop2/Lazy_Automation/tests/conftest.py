"""Pytest configuration for tests."""

from hypothesis import settings, HealthCheck

# Configure Hypothesis for property-based testing
settings.register_profile("default", max_examples=100, suppress_health_check=[HealthCheck.too_slow])
settings.load_profile("default")

"""Tests for the Analytics Engine."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from src.analytics_engine import AnalyticsEngine
from src.data_models import ExecutionRecord, ValidationError


@pytest.fixture
def temp_analytics_dir():
    """Create a temporary directory for analytics data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def analytics_engine(temp_analytics_dir):
    """Create an AnalyticsEngine instance with temporary storage."""
    return AnalyticsEngine(analytics_dir=temp_analytics_dir)


def test_analytics_engine_initialization(temp_analytics_dir):
    """Test AnalyticsEngine initialization."""
    engine = AnalyticsEngine(analytics_dir=temp_analytics_dir)
    assert engine.analytics_dir == Path(temp_analytics_dir)
    assert engine.records_file == Path(temp_analytics_dir) / "execution_records.json"


def test_record_execution(analytics_engine):
    """Test recording an execution."""
    record = analytics_engine.record_execution(
        execution_id="exec_1",
        automation_id="auto_1",
        automation_name="Test Automation",
        success=True,
        duration_seconds=10.5,
        items_processed=5,
        time_saved_minutes=15.0,
    )

    assert record.execution_id == "exec_1"
    assert record.automation_id == "auto_1"
    assert record.success is True
    assert record.items_processed == 5
    assert record.time_saved_minutes == 15.0


def test_record_execution_with_errors(analytics_engine):
    """Test recording an execution with errors."""
    errors = ["File not found", "Permission denied"]
    record = analytics_engine.record_execution(
        execution_id="exec_2",
        automation_id="auto_2",
        automation_name="Failed Automation",
        success=False,
        errors=errors,
    )

    assert record.success is False
    assert len(record.errors) == 2
    assert "File not found" in record.errors


def test_get_execution_history(analytics_engine):
    """Test retrieving execution history."""
    # Record multiple executions
    for i in range(5):
        analytics_engine.record_execution(
            execution_id=f"exec_{i}",
            automation_id="auto_1",
            automation_name="Test Automation",
            success=True,
            items_processed=i + 1,
        )

    history = analytics_engine.get_execution_history()
    assert len(history) == 5
    # Most recent should be first
    assert history[0].execution_id == "exec_4"


def test_get_execution_history_filtered(analytics_engine):
    """Test retrieving execution history filtered by automation ID."""
    # Record executions for different automations
    for i in range(3):
        analytics_engine.record_execution(
            execution_id=f"exec_auto1_{i}",
            automation_id="auto_1",
            automation_name="Automation 1",
            success=True,
        )

    for i in range(2):
        analytics_engine.record_execution(
            execution_id=f"exec_auto2_{i}",
            automation_id="auto_2",
            automation_name="Automation 2",
            success=True,
        )

    history = analytics_engine.get_execution_history(automation_id="auto_1")
    assert len(history) == 3
    assert all(r.automation_id == "auto_1" for r in history)


def test_calculate_time_saved(analytics_engine):
    """Test calculating total time saved."""
    analytics_engine.record_execution(
        execution_id="exec_1",
        automation_id="auto_1",
        automation_name="Test",
        success=True,
        time_saved_minutes=10.0,
    )
    analytics_engine.record_execution(
        execution_id="exec_2",
        automation_id="auto_1",
        automation_name="Test",
        success=True,
        time_saved_minutes=15.0,
    )
    analytics_engine.record_execution(
        execution_id="exec_3",
        automation_id="auto_1",
        automation_name="Test",
        success=False,
        time_saved_minutes=5.0,  # Should not be counted
    )

    total_saved = analytics_engine.calculate_time_saved()
    assert total_saved == 25.0


def test_calculate_time_saved_by_automation(analytics_engine):
    """Test calculating time saved for specific automation."""
    analytics_engine.record_execution(
        execution_id="exec_1",
        automation_id="auto_1",
        automation_name="Test 1",
        success=True,
        time_saved_minutes=10.0,
    )
    analytics_engine.record_execution(
        execution_id="exec_2",
        automation_id="auto_2",
        automation_name="Test 2",
        success=True,
        time_saved_minutes=20.0,
    )

    saved_auto1 = analytics_engine.calculate_time_saved(automation_id="auto_1")
    assert saved_auto1 == 10.0


def test_get_usage_statistics_empty(analytics_engine):
    """Test getting usage statistics with no records."""
    stats = analytics_engine.get_usage_statistics()

    assert stats["total_executions"] == 0
    assert stats["successful_executions"] == 0
    assert stats["failed_executions"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["total_items_processed"] == 0
    assert stats["total_time_saved_minutes"] == 0.0


def test_get_usage_statistics(analytics_engine):
    """Test getting usage statistics."""
    # Record successful executions
    for i in range(3):
        analytics_engine.record_execution(
            execution_id=f"exec_success_{i}",
            automation_id="auto_1",
            automation_name="Test",
            success=True,
            items_processed=10,
            time_saved_minutes=5.0,
            duration_seconds=2.0,
        )

    # Record failed execution
    analytics_engine.record_execution(
        execution_id="exec_fail",
        automation_id="auto_1",
        automation_name="Test",
        success=False,
        items_processed=0,
        duration_seconds=1.0,
    )

    stats = analytics_engine.get_usage_statistics()

    assert stats["total_executions"] == 4
    assert stats["successful_executions"] == 3
    assert stats["failed_executions"] == 1
    assert stats["success_rate"] == 75.0
    assert stats["total_items_processed"] == 30
    assert stats["total_time_saved_minutes"] == 15.0
    assert stats["average_duration_seconds"] == 1.75


def test_get_usage_statistics_per_automation(analytics_engine):
    """Test per-automation statistics."""
    analytics_engine.record_execution(
        execution_id="exec_1",
        automation_id="auto_1",
        automation_name="Automation 1",
        success=True,
        items_processed=5,
        time_saved_minutes=10.0,
    )
    analytics_engine.record_execution(
        execution_id="exec_2",
        automation_id="auto_2",
        automation_name="Automation 2",
        success=True,
        items_processed=10,
        time_saved_minutes=20.0,
    )

    stats = analytics_engine.get_usage_statistics()

    assert "auto_1" in stats["automations"]
    assert "auto_2" in stats["automations"]
    assert stats["automations"]["auto_1"]["executions"] == 1
    assert stats["automations"]["auto_2"]["executions"] == 1


def test_get_error_trends_empty(analytics_engine):
    """Test getting error trends with no records."""
    trends = analytics_engine.get_error_trends()

    assert trends["total_errors"] == 0
    assert trends["error_rate"] == 0.0
    assert len(trends["most_common_errors"]) == 0


def test_get_error_trends(analytics_engine):
    """Test getting error trends."""
    # Record successful executions
    for i in range(7):
        analytics_engine.record_execution(
            execution_id=f"exec_success_{i}",
            automation_id="auto_1",
            automation_name="Test",
            success=True,
        )

    # Record failed executions with errors
    analytics_engine.record_execution(
        execution_id="exec_fail_1",
        automation_id="auto_1",
        automation_name="Test",
        success=False,
        errors=["File not found", "Permission denied"],
    )
    analytics_engine.record_execution(
        execution_id="exec_fail_2",
        automation_id="auto_2",
        automation_name="Test 2",
        success=False,
        errors=["File not found"],
    )

    trends = analytics_engine.get_error_trends()

    assert trends["total_errors"] == 2
    # Error rate should be approximately 20% (2 out of 9 or 10)
    assert 18.0 <= trends["error_rate"] <= 25.0
    assert "auto_1" in trends["errors_by_automation"]
    assert "auto_2" in trends["errors_by_automation"]


def test_get_automation_frequency(analytics_engine):
    """Test getting automation frequency."""
    # Record executions for different automations
    for i in range(5):
        analytics_engine.record_execution(
            execution_id=f"exec_auto1_{i}",
            automation_id="auto_1",
            automation_name="Automation 1",
            success=True,
        )

    for i in range(3):
        analytics_engine.record_execution(
            execution_id=f"exec_auto2_{i}",
            automation_id="auto_2",
            automation_name="Automation 2",
            success=True,
        )

    frequency = analytics_engine.get_automation_frequency()

    assert frequency["auto_1"] == 5
    assert frequency["auto_2"] == 3
    # Should be sorted by frequency descending
    assert list(frequency.keys())[0] == "auto_1"


def test_get_dashboard_summary(analytics_engine):
    """Test getting dashboard summary."""
    analytics_engine.record_execution(
        execution_id="exec_1",
        automation_id="auto_1",
        automation_name="Test",
        success=True,
        items_processed=10,
        time_saved_minutes=5.0,
    )

    summary = analytics_engine.get_dashboard_summary()

    assert "timestamp" in summary
    assert "usage_statistics" in summary
    assert "error_trends" in summary
    assert "automation_frequency" in summary
    assert "recent_executions" in summary


def test_clear_old_records(analytics_engine):
    """Test clearing old records."""
    # Record an old execution (91 days ago)
    old_record = ExecutionRecord(
        execution_id="exec_old",
        automation_id="auto_1",
        automation_name="Old Test",
        timestamp=(datetime.now() - timedelta(days=91)).isoformat(),
        success=True,
    )
    analytics_engine._records.append(old_record)

    # Record a recent execution
    analytics_engine.record_execution(
        execution_id="exec_recent",
        automation_id="auto_1",
        automation_name="Recent Test",
        success=True,
    )

    deleted = analytics_engine.clear_old_records(days=90)

    assert deleted == 1
    assert len(analytics_engine._records) == 1
    assert analytics_engine._records[0].execution_id == "exec_recent"


def test_persistence(temp_analytics_dir):
    """Test that records persist across engine instances."""
    # Create engine and record execution
    engine1 = AnalyticsEngine(analytics_dir=temp_analytics_dir)
    engine1.record_execution(
        execution_id="exec_1",
        automation_id="auto_1",
        automation_name="Test",
        success=True,
        time_saved_minutes=10.0,
    )

    # Create new engine instance and verify record is loaded
    engine2 = AnalyticsEngine(analytics_dir=temp_analytics_dir)
    history = engine2.get_execution_history()

    assert len(history) == 1
    assert history[0].execution_id == "exec_1"
    assert history[0].time_saved_minutes == 10.0


# Property-Based Tests

@given(
    num_executions=st.integers(min_value=1, max_value=20),
    num_automations=st.integers(min_value=1, max_value=5),
)
@settings(deadline=None)
def test_property_analytics_dashboard_display(num_executions, num_automations):
    """
    **Feature: lazy-automation-platform, Property 42: Analytics Dashboard Display**
    
    For any analytics dashboard load, the system should display time saved, usage statistics, and error logs.
    **Validates: Requirements 14.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AnalyticsEngine(analytics_dir=tmpdir)
        
        # Record executions for multiple automations
        for i in range(num_executions):
            automation_id = f"auto_{i % num_automations}"
            engine.record_execution(
                execution_id=f"exec_{i}",
                automation_id=automation_id,
                automation_name=f"Automation {i % num_automations}",
                success=(i % 3) != 0,  # Some failures
                items_processed=i + 1,
                time_saved_minutes=float(i + 1),
                errors=["Test error"] if (i % 3) == 0 else [],
            )
        
        # Get dashboard summary
        summary = engine.get_dashboard_summary()
        
        # Verify dashboard contains all required components
        assert "timestamp" in summary
        assert "usage_statistics" in summary
        assert "error_trends" in summary
        assert "automation_frequency" in summary
        assert "recent_executions" in summary
        
        # Verify usage statistics contains time saved
        stats = summary["usage_statistics"]
        assert "total_time_saved_minutes" in stats
        assert stats["total_time_saved_minutes"] >= 0
        
        # Verify usage statistics contains usage statistics
        assert "total_executions" in stats
        assert "successful_executions" in stats
        assert "failed_executions" in stats
        assert "success_rate" in stats
        assert "automations" in stats
        
        # Verify error trends contains error logs
        errors = summary["error_trends"]
        assert "total_errors" in errors
        assert "error_rate" in errors
        assert "errors_by_automation" in errors
        assert "most_common_errors" in errors


@given(
    time_saved_values=st.lists(
        st.floats(min_value=0, max_value=100),
        min_size=1,
        max_size=50,
    ),
)
def test_property_time_saved_calculation(time_saved_values):
    """
    **Feature: lazy-automation-platform, Property 43: Time Saved Calculation**
    
    For any set of successful executions, the total time saved should equal the sum of individual time saved values.
    **Validates: Requirements 14.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AnalyticsEngine(analytics_dir=tmpdir)

        for i, time_saved in enumerate(time_saved_values):
            engine.record_execution(
                execution_id=f"exec_{i}",
                automation_id="auto_1",
                automation_name="Test",
                success=True,
                time_saved_minutes=time_saved,
            )

        total_saved = engine.calculate_time_saved()
        expected_total = sum(time_saved_values)

        assert abs(total_saved - expected_total) < 0.01  # Allow for floating point precision


@given(
    num_successful=st.integers(min_value=0, max_value=50),
    num_failed=st.integers(min_value=0, max_value=50),
)
@settings(deadline=None)
def test_property_usage_statistics_accuracy(num_successful, num_failed):
    """
    **Feature: lazy-automation-platform, Property 44: Usage Statistics Display**
    
    For any set of executions, the usage statistics should accurately reflect success/failure counts and rates.
    **Validates: Requirements 14.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AnalyticsEngine(analytics_dir=tmpdir)

        # Record successful executions
        for i in range(num_successful):
            engine.record_execution(
                execution_id=f"exec_success_{i}",
                automation_id="auto_1",
                automation_name="Test",
                success=True,
                items_processed=1,
            )

        # Record failed executions
        for i in range(num_failed):
            engine.record_execution(
                execution_id=f"exec_fail_{i}",
                automation_id="auto_1",
                automation_name="Test",
                success=False,
            )

        stats = engine.get_usage_statistics()

        total = num_successful + num_failed
        assert stats["total_executions"] == total
        assert stats["successful_executions"] == num_successful
        assert stats["failed_executions"] == num_failed

        if total > 0:
            expected_rate = (num_successful / total) * 100
            assert abs(stats["success_rate"] - expected_rate) < 0.01


@given(
    num_errors=st.integers(min_value=1, max_value=20),
    num_successes=st.integers(min_value=0, max_value=30),
)
@settings(deadline=None)
def test_property_error_log_display(num_errors, num_successes):
    """
    **Feature: lazy-automation-platform, Property 45: Error Log Display**
    
    For any set of executions with errors, the error trends should accurately report error counts and rates.
    **Validates: Requirements 14.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AnalyticsEngine(analytics_dir=tmpdir)

        # Record successful executions
        for i in range(num_successes):
            engine.record_execution(
                execution_id=f"exec_success_{i}",
                automation_id="auto_1",
                automation_name="Test",
                success=True,
            )

        # Record failed executions with errors
        for i in range(num_errors):
            engine.record_execution(
                execution_id=f"exec_fail_{i}",
                automation_id="auto_1",
                automation_name="Test",
                success=False,
                errors=[f"Error {i}"],
            )

        trends = engine.get_error_trends()

        total = num_errors + num_successes
        assert trends["total_errors"] == num_errors

        if total > 0:
            expected_rate = (num_errors / total) * 100
            assert abs(trends["error_rate"] - expected_rate) < 0.01

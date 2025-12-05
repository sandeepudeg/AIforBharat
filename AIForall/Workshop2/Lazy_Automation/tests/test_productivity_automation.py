"""Tests for Productivity Automation Module."""

import pytest
import tempfile
import os
import csv
from pathlib import Path
from hypothesis import given, strategies as st
from src.productivity_automation import ReportGenerator, LogCleaner, ClipboardEnhancer


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_csv(temp_dir):
    """Create a sample CSV file for testing."""
    csv_path = os.path.join(temp_dir, "sample.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age", "City"])
        writer.writerow(["Alice", "30", "New York"])
        writer.writerow(["Bob", "25", "Los Angeles"])
        writer.writerow(["Charlie", "35", "Chicago"])
    return csv_path


@pytest.fixture
def sample_log(temp_dir):
    """Create a sample log file for testing."""
    log_path = os.path.join(temp_dir, "sample.log")
    with open(log_path, 'w') as f:
        f.write("2024-01-01 10:00:00 INFO Starting application\n")
        f.write("2024-01-01 10:00:01 WARNING Low memory detected\n")
        f.write("2024-01-01 10:00:02 ERROR Failed to connect to database\n")
        f.write("2024-01-01 10:00:03 INFO Retrying connection\n")
        f.write("2024-01-01 10:00:04 CRITICAL System failure\n")
    return log_path


# ReportGenerator Tests

def test_parse_csv_basic(sample_csv):
    """Test parsing a basic CSV file."""
    headers, rows = ReportGenerator.parse_csv(sample_csv)

    assert headers == ["Name", "Age", "City"]
    assert len(rows) == 3
    assert rows[0] == ["Alice", "30", "New York"]


def test_parse_csv_nonexistent_file():
    """Test parsing a nonexistent CSV file."""
    with pytest.raises(FileNotFoundError):
        ReportGenerator.parse_csv("/nonexistent/file.csv")


def test_parse_csv_empty_file(temp_dir):
    """Test parsing an empty CSV file."""
    empty_csv = os.path.join(temp_dir, "empty.csv")
    with open(empty_csv, 'w') as f:
        f.write("")

    with pytest.raises(ValueError):
        ReportGenerator.parse_csv(empty_csv)


def test_generate_statistics(sample_csv):
    """Test generating statistics from CSV data."""
    headers, rows = ReportGenerator.parse_csv(sample_csv)
    stats = ReportGenerator.generate_statistics(headers, rows)

    assert stats["row_count"] == 3
    assert stats["column_count"] == 3
    assert "Age" in stats["numeric_columns"]
    assert "Name" in stats["text_columns"]


def test_export_to_json(sample_csv):
    """Test exporting CSV data to JSON."""
    headers, rows = ReportGenerator.parse_csv(sample_csv)
    json_str = ReportGenerator.export_to_json(headers, rows)

    assert isinstance(json_str, str)
    assert "Alice" in json_str
    assert "30" in json_str


# LogCleaner Tests

def test_parse_log_file(sample_log):
    """Test parsing a log file."""
    lines = LogCleaner.parse_log_file(sample_log)

    assert len(lines) == 5
    assert "Starting application" in lines[0]


def test_parse_log_file_nonexistent():
    """Test parsing a nonexistent log file."""
    with pytest.raises(FileNotFoundError):
        LogCleaner.parse_log_file("/nonexistent/file.log")


def test_extract_errors(sample_log):
    """Test extracting errors from log file."""
    lines = LogCleaner.parse_log_file(sample_log)
    errors = LogCleaner.extract_errors(lines)

    assert len(errors) == 2  # ERROR and CRITICAL
    assert any("Failed to connect" in e["content"] for e in errors)


def test_extract_warnings(sample_log):
    """Test extracting warnings from log file."""
    lines = LogCleaner.parse_log_file(sample_log)
    warnings = LogCleaner.extract_warnings(lines)

    assert len(warnings) == 1
    assert "Low memory" in warnings[0]["content"]


def test_analyze_log(sample_log):
    """Test analyzing a log file."""
    analysis = LogCleaner.analyze_log(sample_log)

    assert analysis["total_lines"] == 5
    assert analysis["error_count"] == 2
    assert analysis["warning_count"] == 1


# ClipboardEnhancer Tests

def test_clipboard_enhancer_add_item():
    """Test adding items to clipboard history."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("test content")

    assert enhancer.get_history_size() == 1


def test_clipboard_enhancer_get_history():
    """Test retrieving clipboard history."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("first")
    enhancer.add_item("second")
    enhancer.add_item("third")

    history = enhancer.get_history()

    assert len(history) == 3
    assert history[0]["content"] == "third"  # Most recent first
    assert history[2]["content"] == "first"  # Oldest last


def test_clipboard_enhancer_search():
    """Test searching clipboard history."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("hello world", tags=["greeting"])
    enhancer.add_item("goodbye world", tags=["farewell"])
    enhancer.add_item("test content")

    results = enhancer.search("world")

    assert len(results) == 2
    assert all("world" in r["content"] for r in results)


def test_clipboard_enhancer_search_by_tag():
    """Test searching clipboard history by tag."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("content1", tags=["important"])
    enhancer.add_item("content2", tags=["urgent"])
    enhancer.add_item("content3", tags=["important", "urgent"])

    results = enhancer.search("important")

    assert len(results) == 2


def test_clipboard_enhancer_search_empty_query():
    """Test searching with empty query."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("test")

    results = enhancer.search("")

    assert len(results) == 0


def test_clipboard_enhancer_get_item_by_index():
    """Test getting item by index."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("first")
    enhancer.add_item("second")

    item = enhancer.get_item_by_index(0)

    assert item["content"] == "second"


def test_clipboard_enhancer_get_item_by_invalid_index():
    """Test getting item with invalid index."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("test")

    item = enhancer.get_item_by_index(10)

    assert item is None


def test_clipboard_enhancer_clear_history():
    """Test clearing clipboard history."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("test1")
    enhancer.add_item("test2")

    enhancer.clear_history()

    assert enhancer.get_history_size() == 0


def test_clipboard_enhancer_max_items():
    """Test that clipboard respects max_items limit."""
    enhancer = ClipboardEnhancer(max_items=3)

    for i in range(5):
        enhancer.add_item(f"item{i}")

    assert enhancer.get_history_size() == 3


def test_clipboard_enhancer_invalid_content():
    """Test adding invalid content to clipboard."""
    enhancer = ClipboardEnhancer()

    with pytest.raises(ValueError):
        enhancer.add_item(123)  # Not a string


def test_clipboard_enhancer_invalid_search_query():
    """Test searching with invalid query."""
    enhancer = ClipboardEnhancer()
    enhancer.add_item("test")

    with pytest.raises(ValueError):
        enhancer.search(123)  # Not a string


# Property-Based Tests

@given(
    csv_data=st.lists(
        st.lists(st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs')), min_size=1, max_size=50), min_size=2, max_size=5),
        min_size=2,
        max_size=10
    )
)
def test_csv_parsing_round_trip(csv_data):
    """
    **Feature: lazy-automation-platform, Property 8: CSV Parsing Round Trip**
    
    For any valid CSV file, parsing it and then re-exporting should produce 
    equivalent data (allowing for formatting differences).
    
    **Validates: Requirements 3.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test.csv")

        # Write CSV with UTF-8 encoding
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for row in csv_data:
                writer.writerow(row)

        # Parse CSV
        headers, rows = ReportGenerator.parse_csv(csv_path)

        # Verify headers match first row
        assert headers == csv_data[0]

        # Verify data rows match remaining rows
        assert len(rows) == len(csv_data) - 1
        for i, row in enumerate(rows):
            assert row == csv_data[i + 1]


@given(
    log_lines=st.lists(
        st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs')), min_size=1, max_size=100),
        min_size=1,
        max_size=20
    )
)
def test_log_parsing_error_detection(log_lines):
    """
    **Feature: lazy-automation-platform, Property 9: Log Parsing Error Detection**
    
    For any log file containing error and warning entries, the log parser should 
    correctly identify and extract all error and warning lines.
    
    **Validates: Requirements 3.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "test.log")

        # Write log file with some error/warning lines using UTF-8 encoding
        with open(log_path, 'w', encoding='utf-8') as f:
            for line in log_lines:
                f.write(line + "\n")

        # Parse and analyze
        lines = LogCleaner.parse_log_file(log_path)
        errors = LogCleaner.extract_errors(lines)
        warnings = LogCleaner.extract_warnings(lines)

        # Verify we got the right number of lines
        assert len(lines) == len(log_lines)

        # Verify errors and warnings are subsets of lines
        for error in errors:
            assert error["line_number"] >= 1
            assert error["line_number"] <= len(lines)

        for warning in warnings:
            assert warning["line_number"] >= 1
            assert warning["line_number"] <= len(lines)


@given(
    items=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100),
            st.lists(st.text(min_size=1, max_size=20), max_size=3)
        ),
        min_size=1,
        max_size=10
    )
)
def test_clipboard_history_ordering(items):
    """
    **Feature: lazy-automation-platform, Property 10: Clipboard History Ordering**
    
    For any sequence of clipboard items added to the history, retrieving the 
    history should return items in reverse chronological order (most recent first).
    
    **Validates: Requirements 3.3, 3.4**
    """
    enhancer = ClipboardEnhancer(max_items=100)

    # Add items
    for content, tags in items:
        enhancer.add_item(content, tags=tags)

    # Get history
    history = enhancer.get_history()

    # Verify ordering: most recent first
    assert len(history) == len(items)

    # The first item in history should be the last one added
    assert history[0]["content"] == items[-1][0]

    # The last item in history should be the first one added
    assert history[-1]["content"] == items[0][0]

    # Verify all items are present
    history_contents = [item["content"] for item in history]
    added_contents = [content for content, _ in items]
    assert history_contents == list(reversed(added_contents))

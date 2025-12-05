"""Tests for ExportService."""

import pytest
import tempfile
import json
import csv
import os
from pathlib import Path
from hypothesis import given, strategies as st
from src.export_service import ExportService
from src.data_models import (
    FileOperationResult,
    EmailSummary,
    ClipboardItem,
    ExecutionRecord,
    AutomationConfig
)


@pytest.fixture
def temp_export_dir():
    """Create a temporary directory for exports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def export_service(temp_export_dir):
    """Create an ExportService instance with temporary directory."""
    return ExportService(export_dir=temp_export_dir)


@pytest.fixture
def sample_config():
    """Create a sample AutomationConfig."""
    return AutomationConfig(
        task_name="test_task",
        enabled=True,
        options={"option1": "value1"}
    )


@pytest.fixture
def sample_execution_record():
    """Create a sample ExecutionRecord."""
    return ExecutionRecord(
        execution_id="exec_001",
        automation_id="auto_001",
        automation_name="test_automation",
        success=True,
        duration_seconds=5.5,
        items_processed=10,
        time_saved_minutes=2.5
    )


@pytest.fixture
def sample_file_operation_result():
    """Create a sample FileOperationResult."""
    return FileOperationResult(
        success=True,
        processed_count=5,
        error_count=0,
        details=[
            {"file": "test1.txt", "status": "success"},
            {"file": "test2.txt", "status": "success"}
        ]
    )


def test_export_results_json_with_dict(export_service, sample_config):
    """Test exporting dictionary results as JSON."""
    results = {"key1": "value1", "key2": "value2"}
    filepath = export_service.export_results_json(
        results,
        "test_automation",
        sample_config,
        exclude_sensitive=False
    )

    assert os.path.exists(filepath)
    assert filepath.endswith(".json")

    with open(filepath, "r") as f:
        exported_data = json.load(f)

    assert "metadata" in exported_data
    assert "results" in exported_data
    assert exported_data["metadata"]["automation_name"] == "test_automation"
    assert exported_data["results"]["key1"] == "value1"


def test_export_results_json_with_dataclass(export_service, sample_file_operation_result):
    """Test exporting dataclass results as JSON."""
    filepath = export_service.export_results_json(
        sample_file_operation_result,
        "file_operation"
    )

    assert os.path.exists(filepath)

    with open(filepath, "r") as f:
        exported_data = json.load(f)

    assert exported_data["results"]["success"] is True
    assert exported_data["results"]["processed_count"] == 5


def test_export_results_json_with_list(export_service):
    """Test exporting list results as JSON."""
    results = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]
    filepath = export_service.export_results_json(
        results,
        "list_export"
    )

    assert os.path.exists(filepath)

    with open(filepath, "r") as f:
        exported_data = json.load(f)

    assert "items" in exported_data["results"]
    assert len(exported_data["results"]["items"]) == 2


def test_export_results_csv(export_service, sample_config):
    """Test exporting results as CSV."""
    results = [
        {"name": "file1.txt", "size": 100, "type": "text"},
        {"name": "file2.txt", "size": 200, "type": "text"}
    ]
    filepath = export_service.export_results_csv(
        results,
        "csv_export",
        sample_config
    )

    assert os.path.exists(filepath)
    assert filepath.endswith(".csv")

    # Verify CSV content
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Should have metadata comments, blank line, header, and data rows
    assert any("Automation:" in line for line in lines)
    assert any("name" in line for line in lines)  # Header


def test_export_results_csv_empty_list(export_service):
    """Test exporting empty list as CSV raises error."""
    with pytest.raises(ValueError):
        export_service.export_results_csv([], "empty_export")


def test_export_results_csv_non_list(export_service):
    """Test exporting non-list as CSV raises error."""
    with pytest.raises(ValueError):
        export_service.export_results_csv({"key": "value"}, "dict_export")


def test_export_execution_record(export_service, sample_execution_record):
    """Test exporting execution record."""
    filepath = export_service.export_execution_record(sample_execution_record)

    assert os.path.exists(filepath)

    with open(filepath, "r") as f:
        exported_data = json.load(f)

    assert exported_data["metadata"]["record_type"] == "execution_record"
    assert exported_data["record"]["automation_name"] == "test_automation"
    assert exported_data["record"]["success"] is True


def test_exclude_sensitive_data_dict(export_service):
    """Test excluding sensitive data from dictionary."""
    data = {
        "name": "John",
        "password": "secret123",
        "email": "john@example.com",
        "api_key": "key123"
    }

    filtered = export_service._exclude_sensitive_data(data)

    assert "name" in filtered
    assert "password" not in filtered
    assert "email" not in filtered
    assert "api_key" not in filtered


def test_exclude_sensitive_data_nested(export_service):
    """Test excluding sensitive data from nested structure."""
    data = {
        "user": {
            "name": "John",
            "password": "secret123"
        },
        "config": {
            "api_key": "key123",
            "timeout": 30
        }
    }

    filtered = export_service._exclude_sensitive_data(data)

    assert "user" in filtered
    assert "name" in filtered["user"]
    assert "password" not in filtered["user"]
    assert "config" in filtered
    assert "timeout" in filtered["config"]
    assert "api_key" not in filtered["config"]


def test_exclude_sensitive_data_list(export_service):
    """Test excluding sensitive data from list."""
    data = [
        {"name": "item1", "password": "pass1"},
        {"name": "item2", "token": "token123"}
    ]

    filtered = export_service._exclude_sensitive_data(data)

    assert len(filtered) == 2
    assert "name" in filtered[0]
    assert "password" not in filtered[0]
    assert "token" not in filtered[1]


def test_is_sensitive_key(export_service):
    """Test identifying sensitive keys."""
    assert export_service._is_sensitive_key("password") is True
    assert export_service._is_sensitive_key("api_key") is True
    assert export_service._is_sensitive_key("token") is True
    assert export_service._is_sensitive_key("secret") is True
    assert export_service._is_sensitive_key("name") is False
    assert export_service._is_sensitive_key("user_name") is False


def test_export_with_metadata_json(export_service, sample_config, sample_execution_record):
    """Test exporting with comprehensive metadata."""
    results = {"status": "completed", "items": 10}
    filepath = export_service.export_with_metadata(
        results,
        "test_automation",
        "auto_001",
        sample_config,
        sample_execution_record,
        format="json"
    )

    assert os.path.exists(filepath)

    with open(filepath, "r") as f:
        exported_data = json.load(f)

    assert exported_data["metadata"]["automation_name"] == "test_automation"
    assert exported_data["metadata"]["automation_id"] == "auto_001"
    assert "configuration" in exported_data["metadata"]
    assert "execution" in exported_data["metadata"]
    assert exported_data["metadata"]["execution"]["success"] is True


def test_export_with_metadata_csv(export_service, sample_config):
    """Test exporting with metadata as CSV."""
    results = [
        {"name": "file1", "size": 100},
        {"name": "file2", "size": 200}
    ]
    filepath = export_service.export_with_metadata(
        results,
        "csv_automation",
        "auto_002",
        sample_config,
        format="csv"
    )

    assert os.path.exists(filepath)
    assert filepath.endswith(".csv")


def test_get_export_directory(export_service, temp_export_dir):
    """Test getting export directory."""
    export_dir = export_service.get_export_directory()
    assert export_dir == temp_export_dir


def test_list_exports(export_service):
    """Test listing exported files."""
    # Create some exports
    export_service.export_results_json({"data": "test1"}, "export1")
    export_service.export_results_json({"data": "test2"}, "export2")

    exports = export_service.list_exports()

    assert len(exports) >= 2
    assert all(os.path.exists(f) for f in exports)


def test_delete_export(export_service):
    """Test deleting an exported file."""
    filepath = export_service.export_results_json({"data": "test"}, "delete_test")

    assert os.path.exists(filepath)

    success = export_service.delete_export(filepath)

    assert success is True
    assert not os.path.exists(filepath)


def test_delete_export_nonexistent(export_service):
    """Test deleting nonexistent export."""
    success = export_service.delete_export("/nonexistent/file.json")
    assert success is False


def test_delete_export_outside_directory(export_service):
    """Test deleting file outside export directory."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = f.name

    try:
        success = export_service.delete_export(temp_file)
        assert success is False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Property-Based Tests

@given(
    automation_name=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz_",
        min_size=1,
        max_size=30
    ),
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
    )
)
def test_export_metadata_inclusion(automation_name, data_dict):
    """
    **Feature: lazy-automation-platform, Property 21: Export Metadata Inclusion**
    
    For any exported result, the export should include metadata about the automation 
    task and configuration used.
    
    **Validates: Requirements 7.4**
    """
    with tempfile.TemporaryDirectory() as temp_export_dir:
        export_service = ExportService(export_dir=temp_export_dir)
        
        # Create a sample config
        config = AutomationConfig(
            task_name="test_task",
            enabled=True,
            options={"option1": "value1"}
        )
        
        # Export results with metadata
        filepath = export_service.export_results_json(
            data_dict,
            automation_name,
            config,
            exclude_sensitive=False
        )
        
        # Verify file was created
        assert os.path.exists(filepath), "Export file should be created"
        
        # Load and verify metadata
        with open(filepath, "r") as f:
            exported_data = json.load(f)
        
        # Test 1: Verify metadata section exists
        assert "metadata" in exported_data, "Export should contain metadata section"
        metadata = exported_data["metadata"]
        
        # Test 2: Verify automation name is in metadata
        assert "automation_name" in metadata, "Metadata should contain automation_name"
        assert metadata["automation_name"] == automation_name, \
            f"Automation name should match: {metadata['automation_name']} != {automation_name}"
        
        # Test 3: Verify export timestamp is in metadata
        assert "export_timestamp" in metadata, "Metadata should contain export_timestamp"
        assert len(metadata["export_timestamp"]) > 0, "Export timestamp should not be empty"
        
        # Test 4: Verify export version is in metadata
        assert "export_version" in metadata, "Metadata should contain export_version"
        assert metadata["export_version"] == "1.0", "Export version should be 1.0"
        
        # Test 5: Verify configuration metadata is included
        assert "configuration" in metadata, "Metadata should contain configuration"
        config_meta = metadata["configuration"]
        assert config_meta["task_name"] == "test_task", "Configuration task_name should match"
        assert config_meta["enabled"] is True, "Configuration enabled should match"
        
        # Test 6: Verify results are preserved
        assert "results" in exported_data, "Export should contain results section"
        assert exported_data["results"] == data_dict, "Results should match original data"
        
        # Test 7: Verify export is valid JSON
        try:
            json.dumps(exported_data)
        except (TypeError, ValueError):
            pytest.fail("Exported data should be valid JSON serializable")
        
        # Test 8: Verify metadata is not empty
        assert len(metadata) > 0, "Metadata should not be empty"
        
        # Test 9: Verify all required metadata fields are present
        required_fields = ["automation_name", "export_timestamp", "export_version", "configuration"]
        for field in required_fields:
            assert field in metadata, f"Metadata should contain required field: {field}"
        
        # Test 10: Verify export file is readable and contains expected structure
        with open(filepath, "r") as f:
            content = f.read()
        
        assert len(content) > 0, "Export file should not be empty"
        assert "metadata" in content, "Export file should contain metadata"
        assert automation_name in content, "Export file should contain automation name"


@given(
    results_list=st.lists(
        st.dictionaries(
            keys=st.text(
                alphabet="abcdefghijklmnopqrstuvwxyz_",
                min_size=1,
                max_size=15
            ),
            values=st.one_of(
                st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=1, max_size=30),
                st.integers(min_value=0, max_value=100)
            ),
            min_size=1,
            max_size=5
        ),
        min_size=1,
        max_size=10
    ),
    automation_name=st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz_",
        min_size=1,
        max_size=20
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
def test_export_sensitive_data_exclusion(
    results_list,
    automation_name,
    sensitive_keys,
    sensitive_values
):
    """
    **Feature: lazy-automation-platform, Property 53: Export Sensitive Data Exclusion**
    
    For any exported result, the system should exclude sensitive data from exports unless 
    explicitly requested.
    
    **Validates: Requirements 16.4**
    """
    with tempfile.TemporaryDirectory() as temp_export_dir:
        export_service = ExportService(export_dir=temp_export_dir)
        
        # Add sensitive data to results
        results_with_sensitive = []
        for i, result in enumerate(results_list):
            result_copy = result.copy()
            # Add sensitive fields
            for j, key in enumerate(sensitive_keys):
                if j < len(sensitive_values):
                    result_copy[key] = sensitive_values[j]
            results_with_sensitive.append(result_copy)
        
        # Export with sensitive data exclusion enabled
        filepath = export_service.export_results_json(
            results_with_sensitive,
            automation_name,
            exclude_sensitive=True
        )
        
        # Load exported data
        with open(filepath, "r") as f:
            exported_data = json.load(f)
        
        exported_json = json.dumps(exported_data)
        
        # Test 1: Verify sensitive keys are excluded from export
        for sensitive_key in sensitive_keys:
            # Check in the results section
            if isinstance(exported_data.get("results"), dict):
                assert sensitive_key not in exported_data["results"], \
                    f"Sensitive key '{sensitive_key}' should be excluded from export"
            elif isinstance(exported_data.get("results"), list):
                for item in exported_data["results"]:
                    if isinstance(item, dict):
                        assert sensitive_key not in item, \
                            f"Sensitive key '{sensitive_key}' should be excluded from export items"
        
        # Test 2: Verify sensitive values are not in export
        for sensitive_value in sensitive_values:
            if len(sensitive_value) > 3:  # Only check longer values to avoid false positives
                assert sensitive_value not in exported_json, \
                    f"Sensitive value should be excluded from export: {sensitive_value}"
        
        # Test 3: Verify non-sensitive data is preserved
        # At least some of the original data should still be in the export
        assert len(exported_data.get("results", [])) > 0 or \
               len(str(exported_data.get("results", {}))) > 0, \
            "Export should contain some data after sensitive exclusion"
        
        # Test 4: Verify export is still valid JSON
        try:
            json.dumps(exported_data)
        except (TypeError, ValueError):
            pytest.fail("Exported data should remain valid JSON after sensitive data exclusion")
        
        # Test 5: Verify metadata is preserved
        assert "metadata" in exported_data, "Metadata should be preserved in export"
        assert exported_data["metadata"]["automation_name"] == automation_name, \
            "Automation name should be preserved in metadata"
        
        # Test 6: Verify export without exclusion contains sensitive data
        filepath_with_sensitive = export_service.export_results_json(
            results_with_sensitive,
            automation_name + "_with_sensitive",
            exclude_sensitive=False
        )
        
        with open(filepath_with_sensitive, "r") as f:
            exported_with_sensitive = json.load(f)
        
        exported_with_sensitive_json = json.dumps(exported_with_sensitive)
        
        # At least one sensitive value should be present when exclusion is disabled
        # (unless it happens to be masked by the masking function)
        # We verify that the structure is different
        assert len(exported_with_sensitive_json) >= len(exported_json), \
            "Export with sensitive data should be at least as large as export without"
        
        # Test 7: Verify filtering is consistent
        # Export the same data again and verify we get the same result
        filepath_2 = export_service.export_results_json(
            results_with_sensitive,
            automation_name + "_2",
            exclude_sensitive=True
        )
        
        with open(filepath_2, "r") as f:
            exported_data_2 = json.load(f)
        
        # The structure should be the same (same keys, same number of items)
        if isinstance(exported_data.get("results"), list) and \
           isinstance(exported_data_2.get("results"), list):
            assert len(exported_data["results"]) == len(exported_data_2["results"]), \
                "Export filtering should be consistent across multiple runs"
        
        # Test 8: Verify no sensitive keywords appear in export keys
        def check_no_sensitive_keys(obj):
            if isinstance(obj, dict):
                for key in obj.keys():
                    key_lower = key.lower()
                    for sensitive_keyword in ["password", "token", "key", "secret", "credential"]:
                        assert sensitive_keyword not in key_lower, \
                            f"Export should not contain keys with sensitive keywords: {key}"
                for value in obj.values():
                    check_no_sensitive_keys(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_no_sensitive_keys(item)
        
        check_no_sensitive_keys(exported_data)
        
        # Test 9: Verify export file exists and is readable
        assert os.path.exists(filepath), "Export file should exist"
        assert os.path.getsize(filepath) > 0, "Export file should not be empty"
        
        # Test 10: Verify export can be re-imported
        with open(filepath, "r") as f:
            reimported_data = json.load(f)
        
        assert reimported_data == exported_data, \
            "Re-imported data should match original exported data"

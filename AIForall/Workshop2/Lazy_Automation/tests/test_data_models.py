"""Tests for data models."""

import pytest
import json
from src.data_models import (
    AutomationConfig,
    FileOperationResult,
    EmailSummary,
    ClipboardItem,
    ScheduledTask,
    WorkflowChain,
    CustomRule,
    AutomationBackup,
    ValidationError,
)


def test_automation_config_creation():
    """Test creating an AutomationConfig."""
    config = AutomationConfig(
        task_name="test_task",
        enabled=True,
        options={"option1": "value1"}
    )
    
    assert config.task_name == "test_task"
    assert config.enabled is True
    assert config.options["option1"] == "value1"


def test_automation_config_serialization():
    """Test AutomationConfig JSON serialization and deserialization."""
    config = AutomationConfig(
        task_name="test_task",
        enabled=True,
        options={"option1": "value1"}
    )
    
    json_str = config.to_json()
    loaded_config = AutomationConfig.from_json(json_str)
    
    assert loaded_config.task_name == config.task_name
    assert loaded_config.enabled == config.enabled
    assert loaded_config.options == config.options


def test_file_operation_result_creation():
    """Test creating a FileOperationResult."""
    result = FileOperationResult(
        success=True,
        processed_count=10,
        error_count=0,
        details=[{"file": "test.txt", "status": "success"}],
        download_path="/path/to/download"
    )
    
    assert result.success is True
    assert result.processed_count == 10
    assert result.error_count == 0


def test_file_operation_result_serialization():
    """Test FileOperationResult JSON serialization."""
    result = FileOperationResult(
        success=True,
        processed_count=5,
        error_count=1,
        details=[{"file": "test.txt"}]
    )
    
    json_str = result.to_json()
    loaded_result = FileOperationResult.from_json(json_str)
    
    assert loaded_result.success == result.success
    assert loaded_result.processed_count == result.processed_count


def test_email_summary_creation():
    """Test creating an EmailSummary."""
    summary = EmailSummary(
        sender="test@example.com",
        subject="Test Subject",
        summary="This is a summary",
        original_length=100,
        summary_length=20
    )
    
    assert summary.sender == "test@example.com"
    assert summary.summary_length < summary.original_length


def test_clipboard_item_creation():
    """Test creating a ClipboardItem."""
    item = ClipboardItem(
        content="clipboard content",
        source_task="test_task",
        tags=["tag1", "tag2"]
    )
    
    assert item.content == "clipboard content"
    assert len(item.tags) == 2


def test_scheduled_task_creation():
    """Test creating a ScheduledTask."""
    task = ScheduledTask(
        task_id="task_1",
        task_name="daily_cleanup",
        schedule="0 0 * * *",
        enabled=True
    )
    
    assert task.task_id == "task_1"
    assert task.enabled is True


def test_workflow_chain_creation():
    """Test creating a WorkflowChain."""
    chain = WorkflowChain(
        chain_id="chain_1",
        name="cleanup_workflow",
        tasks=["task1", "task2", "task3"],
        enabled=True
    )
    
    assert chain.chain_id == "chain_1"
    assert len(chain.tasks) == 3


def test_custom_rule_creation():
    """Test creating a CustomRule."""
    rule = CustomRule(
        rule_id="rule_1",
        name="archive_old_files",
        conditions={"file_age": ">30days"},
        actions=[{"action": "move", "destination": "archive"}],
        enabled=True
    )
    
    assert rule.rule_id == "rule_1"
    assert rule.enabled is True


def test_automation_backup_creation():
    """Test creating an AutomationBackup."""
    backup = AutomationBackup(
        backup_id="backup_1",
        automation_id="auto_1",
        affected_files=["file1.txt", "file2.txt"],
        backup_location="/backups/backup_1"
    )
    
    assert backup.backup_id == "backup_1"
    assert len(backup.affected_files) == 2
    assert backup.can_rollback is True


# Validation tests

def test_automation_config_validation_empty_task_name():
    """Test that AutomationConfig rejects empty task_name."""
    with pytest.raises(ValidationError):
        AutomationConfig(task_name="", enabled=True)


def test_automation_config_validation_invalid_enabled():
    """Test that AutomationConfig rejects non-boolean enabled."""
    with pytest.raises(ValidationError):
        AutomationConfig(task_name="test", enabled="true")


def test_file_operation_result_validation_negative_count():
    """Test that FileOperationResult rejects negative counts."""
    with pytest.raises(ValidationError):
        FileOperationResult(success=True, processed_count=-1, error_count=0)


def test_email_summary_validation_empty_sender():
    """Test that EmailSummary rejects empty sender."""
    with pytest.raises(ValidationError):
        EmailSummary(sender="", subject="test", summary="test", original_length=10, summary_length=5)


def test_clipboard_item_validation_invalid_tags():
    """Test that ClipboardItem rejects non-string tags."""
    with pytest.raises(ValidationError):
        ClipboardItem(content="test", tags=[1, 2, 3])


def test_scheduled_task_validation_empty_task_id():
    """Test that ScheduledTask rejects empty task_id."""
    with pytest.raises(ValidationError):
        ScheduledTask(task_id="", task_name="test", schedule="0 0 * * *", enabled=True)


def test_workflow_chain_validation_invalid_tasks():
    """Test that WorkflowChain rejects non-string tasks."""
    with pytest.raises(ValidationError):
        WorkflowChain(chain_id="chain_1", name="test", tasks=[1, 2, 3], enabled=True)


def test_custom_rule_validation_invalid_actions():
    """Test that CustomRule rejects non-dict actions."""
    with pytest.raises(ValidationError):
        CustomRule(
            rule_id="rule_1",
            name="test",
            conditions={"test": "value"},
            actions=["not_a_dict"],
            enabled=True
        )


def test_automation_backup_validation_empty_backup_id():
    """Test that AutomationBackup rejects empty backup_id."""
    with pytest.raises(ValidationError):
        AutomationBackup(backup_id="", automation_id="auto_1")

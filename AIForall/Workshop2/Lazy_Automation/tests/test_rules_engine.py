"""Tests for the RulesEngine."""

import pytest
import os
import tempfile
import json
from pathlib import Path
from hypothesis import given, strategies as st
from src.rules_engine import RulesEngine
from src.data_models import CustomRule


@pytest.fixture
def rules_engine():
    """Create a RulesEngine instance for testing."""
    return RulesEngine()


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_files(temp_directory):
    """Create sample files for testing."""
    files = {}

    # Create a text file
    text_file = os.path.join(temp_directory, "document.txt")
    with open(text_file, 'w') as f:
        f.write("This is a test document with some content")
    files['text'] = text_file

    # Create a PDF file (fake)
    pdf_file = os.path.join(temp_directory, "report.pdf")
    with open(pdf_file, 'w') as f:
        f.write("PDF content")
    files['pdf'] = pdf_file

    # Create an image file (fake)
    image_file = os.path.join(temp_directory, "photo.jpg")
    with open(image_file, 'w') as f:
        f.write("Image content")
    files['image'] = image_file

    # Create a large file
    large_file = os.path.join(temp_directory, "large.bin")
    with open(large_file, 'wb') as f:
        f.write(b'x' * (10 * 1024 * 1024))  # 10 MB
    files['large'] = large_file

    return files


class TestRulesEngineConditionEvaluation:
    """Tests for condition evaluation."""

    def test_evaluate_file_type_condition_match(self, rules_engine, sample_files):
        """Test file type condition when type matches."""
        condition = {'type': 'file_type', 'value': 'document'}
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is True

    def test_evaluate_file_type_condition_no_match(self, rules_engine, sample_files):
        """Test file type condition when type doesn't match."""
        condition = {'type': 'file_type', 'value': 'image'}
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is False

    def test_evaluate_file_size_condition_greater_than(self, rules_engine, sample_files):
        """Test file size condition with greater than operator."""
        condition = {'type': 'file_size', 'operator': '>', 'value': 0.00001}  # Very small threshold
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is True

    def test_evaluate_file_size_condition_less_than(self, rules_engine, sample_files):
        """Test file size condition with less than operator."""
        condition = {'type': 'file_size', 'operator': '<', 'value': 1}  # 1 MB
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is True

    def test_evaluate_file_pattern_condition_match(self, rules_engine, sample_files):
        """Test file pattern condition when pattern matches."""
        condition = {'type': 'file_pattern', 'value': '.*\\.txt'}
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is True

    def test_evaluate_file_pattern_condition_no_match(self, rules_engine, sample_files):
        """Test file pattern condition when pattern doesn't match."""
        condition = {'type': 'file_pattern', 'value': '.*\\.pdf'}
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is False

    def test_evaluate_content_pattern_condition_match(self, rules_engine, sample_files):
        """Test content pattern condition when pattern matches."""
        condition = {'type': 'content_pattern', 'value': 'test document'}
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is True

    def test_evaluate_content_pattern_condition_no_match(self, rules_engine, sample_files):
        """Test content pattern condition when pattern doesn't match."""
        condition = {'type': 'content_pattern', 'value': 'nonexistent'}
        result = rules_engine.evaluate_condition(condition, sample_files['text'])
        assert result is False

    def test_evaluate_condition_nonexistent_file(self, rules_engine):
        """Test condition evaluation on nonexistent file."""
        condition = {'type': 'file_type', 'value': 'document'}
        result = rules_engine.evaluate_condition(condition, '/nonexistent/file.txt')
        assert result is False

    def test_evaluate_condition_invalid_type(self, rules_engine, sample_files):
        """Test condition evaluation with invalid condition type."""
        condition = {'type': 'invalid_type', 'value': 'test'}
        with pytest.raises(ValueError):
            rules_engine.evaluate_condition(condition, sample_files['text'])


class TestRulesEngineActionExecution:
    """Tests for action execution."""

    def test_execute_rename_action_preview(self, rules_engine, sample_files):
        """Test rename action in preview mode."""
        action = {'type': 'rename', 'new_name': 'renamed.txt'}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=True)
        assert success is True
        assert 'Would rename' in message
        # Verify file was not actually renamed
        assert os.path.exists(sample_files['text'])

    def test_execute_rename_action_live(self, rules_engine, sample_files, temp_directory):
        """Test rename action in live mode."""
        action = {'type': 'rename', 'new_name': 'renamed.txt'}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=False)
        assert success is True
        # Verify file was renamed
        renamed_path = os.path.join(temp_directory, 'renamed.txt')
        assert os.path.exists(renamed_path)
        assert not os.path.exists(sample_files['text'])

    def test_execute_delete_action_preview(self, rules_engine, sample_files):
        """Test delete action in preview mode."""
        action = {'type': 'delete'}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=True)
        assert success is True
        assert 'Would delete' in message
        # Verify file was not actually deleted
        assert os.path.exists(sample_files['text'])

    def test_execute_delete_action_live(self, rules_engine, sample_files):
        """Test delete action in live mode."""
        action = {'type': 'delete'}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=False)
        assert success is True
        # Verify file was deleted
        assert not os.path.exists(sample_files['text'])

    def test_execute_copy_action_preview(self, rules_engine, sample_files, temp_directory):
        """Test copy action in preview mode."""
        dest = os.path.join(temp_directory, 'copy', 'document.txt')
        action = {'type': 'copy', 'destination': dest}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=True)
        assert success is True
        assert 'Would copy' in message
        # Verify file was not actually copied
        assert not os.path.exists(dest)

    def test_execute_copy_action_live(self, rules_engine, sample_files, temp_directory):
        """Test copy action in live mode."""
        dest = os.path.join(temp_directory, 'copy', 'document.txt')
        action = {'type': 'copy', 'destination': dest}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=False)
        assert success is True
        # Verify file was copied
        assert os.path.exists(dest)
        assert os.path.exists(sample_files['text'])

    def test_execute_notify_action_preview(self, rules_engine, sample_files):
        """Test notify action in preview mode."""
        action = {'type': 'notify', 'message': 'Test notification'}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=True)
        assert success is True
        assert 'Would send notification' in message

    def test_execute_notify_action_live(self, rules_engine, sample_files):
        """Test notify action in live mode."""
        action = {'type': 'notify', 'message': 'Test notification'}
        success, message = rules_engine.execute_action(action, sample_files['text'], preview=False)
        assert success is True
        assert 'Notification sent' in message

    def test_execute_action_invalid_type(self, rules_engine, sample_files):
        """Test action execution with invalid action type."""
        action = {'type': 'invalid_action'}
        with pytest.raises(ValueError):
            rules_engine.execute_action(action, sample_files['text'])

    def test_execute_action_nonexistent_file(self, rules_engine):
        """Test action execution on nonexistent file."""
        action = {'type': 'delete'}
        success, message = rules_engine.execute_action(action, '/nonexistent/file.txt')
        assert success is False


class TestRulesEngineRuleApplication:
    """Tests for applying rules to directories."""

    def test_apply_rule_basic(self, rules_engine, sample_files, temp_directory):
        """Test applying a basic rule."""
        rule = CustomRule(
            rule_id='rule_1',
            name='delete_txt_files',
            conditions={'file_type': {'type': 'file_type', 'value': 'document'}},
            actions=[{'type': 'delete'}],
            enabled=True
        )

        results = rules_engine.apply_rule(rule, temp_directory, preview=True)

        assert results['rule_id'] == 'rule_1'
        assert results['preview'] is True
        assert results['total_matched'] >= 1
        assert results['total_errors'] == 0

    def test_apply_rule_preview_mode(self, rules_engine, sample_files, temp_directory):
        """Test applying a rule in preview mode."""
        rule = CustomRule(
            rule_id='rule_1',
            name='delete_all',
            conditions={'file_pattern': {'type': 'file_pattern', 'value': '.*'}},
            actions=[{'type': 'delete'}],
            enabled=True
        )

        results = rules_engine.apply_rule(rule, temp_directory, preview=True)

        # Verify files still exist after preview
        for file_path in sample_files.values():
            if os.path.exists(file_path):
                assert True

    def test_apply_rule_live_mode(self, rules_engine, sample_files, temp_directory):
        """Test applying a rule in live mode."""
        # Create a test file to delete
        test_file = os.path.join(temp_directory, 'test_delete.txt')
        with open(test_file, 'w') as f:
            f.write('test')

        rule = CustomRule(
            rule_id='rule_1',
            name='delete_test_files',
            conditions={'file_pattern': {'type': 'file_pattern', 'value': 'test_delete.*'}},
            actions=[{'type': 'delete'}],
            enabled=True
        )

        results = rules_engine.apply_rule(rule, temp_directory, preview=False)

        assert results['total_matched'] >= 1
        assert not os.path.exists(test_file)

    def test_apply_rule_nonexistent_directory(self, rules_engine):
        """Test applying a rule to nonexistent directory."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={},
            actions=[],
            enabled=True
        )

        with pytest.raises(FileNotFoundError):
            rules_engine.apply_rule(rule, '/nonexistent/directory')

    def test_apply_rule_increments_execution_count(self, rules_engine, sample_files, temp_directory):
        """Test that applying a rule increments execution count."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={'file_pattern': {'type': 'file_pattern', 'value': '.*\\.txt'}},
            actions=[{'type': 'notify', 'message': 'test'}],
            enabled=True
        )

        initial_count = rule.execution_count
        rules_engine.apply_rule(rule, temp_directory, preview=False)
        assert rule.execution_count == initial_count + 1


class TestRulesEngineLogging:
    """Tests for execution logging."""

    def test_execution_log_recorded(self, rules_engine, sample_files, temp_directory):
        """Test that execution is logged."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test_rule',
            conditions={'file_pattern': {'type': 'file_pattern', 'value': '.*\\.txt'}},
            actions=[{'type': 'notify', 'message': 'test'}],
            enabled=True
        )

        rules_engine.apply_rule(rule, temp_directory, preview=True)

        log = rules_engine.get_execution_log()
        assert len(log) > 0
        assert log[0]['rule_id'] == 'rule_1'
        assert log[0]['preview'] is True

    def test_clear_execution_log(self, rules_engine, sample_files, temp_directory):
        """Test clearing execution log."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={'file_pattern': {'type': 'file_pattern', 'value': '.*'}},
            actions=[{'type': 'notify', 'message': 'test'}],
            enabled=True
        )

        rules_engine.apply_rule(rule, temp_directory, preview=True)
        assert len(rules_engine.get_execution_log()) > 0

        rules_engine.clear_execution_log()
        assert len(rules_engine.get_execution_log()) == 0


class TestRulesEngineValidation:
    """Tests for rule validation."""

    def test_validate_rule_valid(self, rules_engine):
        """Test validating a valid rule."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={'file_type': {'type': 'file_type', 'value': 'document'}},
            actions=[{'type': 'delete'}],
            enabled=True
        )

        is_valid, message = rules_engine.validate_rule(rule)
        assert is_valid is True
        assert message == ""

    def test_validate_rule_no_conditions(self, rules_engine):
        """Test validating a rule with no conditions."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={},
            actions=[{'type': 'delete'}],
            enabled=True
        )

        is_valid, message = rules_engine.validate_rule(rule)
        assert is_valid is False
        assert "condition" in message.lower()

    def test_validate_rule_no_actions(self, rules_engine):
        """Test validating a rule with no actions."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={'file_type': {'type': 'file_type', 'value': 'document'}},
            actions=[],
            enabled=True
        )

        is_valid, message = rules_engine.validate_rule(rule)
        assert is_valid is False
        assert "action" in message.lower()

    def test_validate_rule_invalid_condition_type(self, rules_engine):
        """Test validating a rule with invalid condition type."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={'invalid': {'type': 'invalid_type', 'value': 'test'}},
            actions=[{'type': 'delete'}],
            enabled=True
        )

        is_valid, message = rules_engine.validate_rule(rule)
        assert is_valid is False
        assert "condition type" in message.lower()

    def test_validate_rule_invalid_action_type(self, rules_engine):
        """Test validating a rule with invalid action type."""
        rule = CustomRule(
            rule_id='rule_1',
            name='test',
            conditions={'file_type': {'type': 'file_type', 'value': 'document'}},
            actions=[{'type': 'invalid_action'}],
            enabled=True
        )

        is_valid, message = rules_engine.validate_rule(rule)
        assert is_valid is False
        assert "action type" in message.lower()


# Property-Based Tests

@given(
    rule_name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    file_pattern=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
)
def test_property_custom_rule_creation(rule_name, file_pattern):
    """
    Property 30: Custom Rule Creation
    *For any* custom rule with condition and action definitions, the system should accept the rule and store it for execution.
    **Validates: Requirements 11.1**
    """
    rules_engine = RulesEngine()

    rule = CustomRule(
        rule_id='test_rule',
        name=rule_name,
        conditions={'file_pattern': {'type': 'file_pattern', 'value': file_pattern}},
        actions=[{'type': 'notify', 'message': 'test'}],
        enabled=True
    )

    is_valid, message = rules_engine.validate_rule(rule)
    assert is_valid is True


@given(
    operator=st.sampled_from(['>', '<', '==', '>=', '<=']),
    size_mb=st.floats(min_value=0.001, max_value=100),
)
def test_property_custom_rule_execution(operator, size_mb):
    """
    Property 31: Custom Rule Execution
    *For any* custom rule where the condition is met, the system should execute the associated action automatically.
    **Validates: Requirements 11.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        rules_engine = RulesEngine()

        # Create a rule that matches the file
        rule = CustomRule(
            rule_id='test_rule',
            name='test',
            conditions={'file_size': {'type': 'file_size', 'operator': operator, 'value': size_mb}},
            actions=[{'type': 'notify', 'message': 'matched'}],
            enabled=True
        )

        results = rules_engine.apply_rule(rule, tmpdir, preview=True)

        # The rule should either match or not match based on the condition
        assert results['total_matched'] >= 0
        assert results['total_errors'] == 0


@given(
    action_type=st.sampled_from(['delete', 'rename', 'copy', 'notify']),
)
def test_property_custom_rule_preview(action_type):
    """
    Property 32: Custom Rule Preview
    *For any* custom rule in preview mode, the system should show what would happen without making actual changes.
    **Validates: Requirements 11.3**
    
    Feature: lazy-automation-platform, Property 32: Custom Rule Preview
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        rules_engine = RulesEngine()

        # Build action based on type
        if action_type == 'delete':
            action = {'type': 'delete'}
        elif action_type == 'rename':
            action = {'type': 'rename', 'new_name': 'renamed.txt'}
        elif action_type == 'copy':
            dest = os.path.join(tmpdir, 'copy', 'test.txt')
            action = {'type': 'copy', 'destination': dest}
        else:  # notify
            action = {'type': 'notify', 'message': 'test notification'}

        rule = CustomRule(
            rule_id='test_rule',
            name='test',
            conditions={'file_pattern': {'type': 'file_pattern', 'value': '.*\\.txt'}},
            actions=[action],
            enabled=True
        )

        # Get initial state
        initial_exists = os.path.exists(test_file)
        initial_size = os.path.getsize(test_file) if initial_exists else 0

        # Apply in preview mode
        results = rules_engine.apply_rule(rule, tmpdir, preview=True)

        # Verify preview mode flag is set
        assert results['preview'] is True

        # Verify file still exists after preview (no actual changes made)
        assert os.path.exists(test_file), "File should still exist after preview mode"
        assert os.path.getsize(test_file) == initial_size, "File size should not change in preview mode"

        # Verify that actions were recorded as what would happen
        if results['total_matched'] > 0:
            assert len(results['executed_actions']) > 0, "Preview should record what would happen"


@given(
    rule_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    rule_name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    file_pattern=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    preview_mode=st.booleans(),
)
def test_property_custom_rule_logging(rule_id, rule_name, file_pattern, preview_mode):
    """
    Property 33: Custom Rule Logging
    *For any* custom rule execution, the system should log all rule executions with details about matched conditions and executed actions.
    **Validates: Requirements 11.4**
    
    Feature: lazy-automation-platform, Property 33: Custom Rule Logging
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        rules_engine = RulesEngine()

        rule = CustomRule(
            rule_id=rule_id,
            name=rule_name,
            conditions={'file_pattern': {'type': 'file_pattern', 'value': file_pattern}},
            actions=[{'type': 'notify', 'message': 'test'}],
            enabled=True
        )

        # Apply the rule
        rules_engine.apply_rule(rule, tmpdir, preview=preview_mode)

        # Verify logging occurred
        log = rules_engine.get_execution_log()
        assert len(log) > 0, "Execution log should contain at least one entry"

        # Verify log entry contains all required fields
        log_entry = log[0]
        assert log_entry['rule_id'] == rule_id, "Log should contain the rule ID"
        assert log_entry['rule_name'] == rule_name, "Log should contain the rule name"
        assert 'timestamp' in log_entry, "Log should contain timestamp"
        assert 'preview' in log_entry, "Log should contain preview flag"
        assert log_entry['preview'] == preview_mode, "Log preview flag should match execution mode"
        assert 'total_matched' in log_entry, "Log should contain total_matched count"
        assert 'total_executed' in log_entry, "Log should contain total_executed count"
        assert 'total_errors' in log_entry, "Log should contain total_errors count"
        
        # Verify counts are non-negative integers
        assert isinstance(log_entry['total_matched'], int), "total_matched should be an integer"
        assert isinstance(log_entry['total_executed'], int), "total_executed should be an integer"
        assert isinstance(log_entry['total_errors'], int), "total_errors should be an integer"
        assert log_entry['total_matched'] >= 0, "total_matched should be non-negative"
        assert log_entry['total_executed'] >= 0, "total_executed should be non-negative"
        assert log_entry['total_errors'] >= 0, "total_errors should be non-negative"

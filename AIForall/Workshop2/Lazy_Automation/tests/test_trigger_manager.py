"""Tests for the trigger manager module."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, HealthCheck, settings
from src.trigger_manager import TriggerManager, TriggerType, Trigger
from src.data_models import ValidationError


class TestTriggerManagerBasic:
    """Basic unit tests for TriggerManager."""

    def test_trigger_manager_initialization(self, tmp_path):
        """Test that trigger manager initializes correctly."""
        manager = TriggerManager(config_dir=str(tmp_path))
        assert manager is not None
        assert len(manager.get_all_triggers()) == 0
        assert len(manager.get_execution_log()) == 0

    def test_register_automation(self, tmp_path):
        """Test registering an automation."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)
        assert "automation_1" in manager._automation_callbacks

    def test_register_automation_invalid_id(self, tmp_path):
        """Test registering automation with invalid ID raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        with pytest.raises(ValidationError):
            manager.register_automation("", callback)

    def test_unregister_automation(self, tmp_path):
        """Test unregistering an automation."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)
        assert "automation_1" in manager._automation_callbacks

        manager.unregister_automation("automation_1")
        assert "automation_1" not in manager._automation_callbacks

    def test_unregister_nonexistent_automation(self, tmp_path):
        """Test unregistering nonexistent automation raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))

        with pytest.raises(ValueError):
            manager.unregister_automation("nonexistent")

    def test_create_file_added_trigger(self, tmp_path):
        """Test creating a FILE_ADDED trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir},
            enabled=True
        )

        assert trigger.trigger_id == "trigger_1"
        assert trigger.trigger_type == TriggerType.FILE_ADDED
        assert trigger.automation_id == "automation_1"
        assert trigger.enabled is True

    def test_create_new_email_trigger(self, tmp_path):
        """Test creating a NEW_EMAIL trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={},
            enabled=True
        )

        assert trigger.trigger_id == "trigger_1"
        assert trigger.trigger_type == TriggerType.NEW_EMAIL

    def test_create_time_based_trigger(self, tmp_path):
        """Test creating a TIME_BASED trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="time_based",
            automation_id="automation_1",
            config={},
            enabled=True
        )

        assert trigger.trigger_id == "trigger_1"
        assert trigger.trigger_type == TriggerType.TIME_BASED

    def test_create_trigger_duplicate_id(self, tmp_path):
        """Test creating trigger with duplicate ID raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir}
        )

        with pytest.raises(ValidationError):
            manager.create_trigger(
                trigger_id="trigger_1",
                trigger_type="file_added",
                automation_id="automation_1",
                config={"watch_path": watch_dir}
            )

    def test_create_trigger_unregistered_automation(self, tmp_path):
        """Test creating trigger with unregistered automation raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        with pytest.raises(ValidationError):
            manager.create_trigger(
                trigger_id="trigger_1",
                trigger_type="file_added",
                automation_id="nonexistent",
                config={"watch_path": watch_dir}
            )

    def test_create_trigger_invalid_type(self, tmp_path):
        """Test creating trigger with invalid type raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        with pytest.raises(ValidationError):
            manager.create_trigger(
                trigger_id="trigger_1",
                trigger_type="invalid_type",
                automation_id="automation_1",
                config={}
            )

    def test_create_file_added_trigger_missing_watch_path(self, tmp_path):
        """Test creating FILE_ADDED trigger without watch_path raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        with pytest.raises(ValidationError):
            manager.create_trigger(
                trigger_id="trigger_1",
                trigger_type="file_added",
                automation_id="automation_1",
                config={}
            )

    def test_delete_trigger(self, tmp_path):
        """Test deleting a trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir}
        )

        assert len(manager.get_all_triggers()) == 1

        manager.delete_trigger("trigger_1")
        assert len(manager.get_all_triggers()) == 0

    def test_delete_nonexistent_trigger(self, tmp_path):
        """Test deleting nonexistent trigger raises error."""
        manager = TriggerManager(config_dir=str(tmp_path))

        with pytest.raises(ValueError):
            manager.delete_trigger("nonexistent")

    def test_enable_trigger(self, tmp_path):
        """Test enabling a disabled trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir},
            enabled=False
        )

        trigger = manager.get_trigger("trigger_1")
        assert trigger.enabled is False

        manager.enable_trigger("trigger_1")
        trigger = manager.get_trigger("trigger_1")
        assert trigger.enabled is True

    def test_disable_trigger(self, tmp_path):
        """Test disabling an enabled trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir},
            enabled=True
        )

        trigger = manager.get_trigger("trigger_1")
        assert trigger.enabled is True

        manager.disable_trigger("trigger_1")
        trigger = manager.get_trigger("trigger_1")
        assert trigger.enabled is False

    def test_get_trigger(self, tmp_path):
        """Test retrieving a trigger by ID."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir}
        )

        trigger = manager.get_trigger("trigger_1")
        assert trigger is not None
        assert trigger.trigger_id == "trigger_1"

    def test_get_nonexistent_trigger(self, tmp_path):
        """Test retrieving nonexistent trigger returns None."""
        manager = TriggerManager(config_dir=str(tmp_path))
        trigger = manager.get_trigger("nonexistent")
        assert trigger is None

    def test_get_all_triggers(self, tmp_path):
        """Test retrieving all triggers."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock()

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        for i in range(3):
            manager.create_trigger(
                trigger_id=f"trigger_{i}",
                trigger_type="file_added",
                automation_id="automation_1",
                config={"watch_path": watch_dir}
            )

        triggers = manager.get_all_triggers()
        assert len(triggers) == 3

    def test_get_triggers_for_automation(self, tmp_path):
        """Test retrieving triggers for a specific automation."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback1 = Mock()
        callback2 = Mock()

        manager.register_automation("automation_1", callback1)
        manager.register_automation("automation_2", callback2)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir}
        )

        manager.create_trigger(
            trigger_id="trigger_2",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir}
        )

        manager.create_trigger(
            trigger_id="trigger_3",
            trigger_type="file_added",
            automation_id="automation_2",
            config={"watch_path": watch_dir}
        )

        triggers = manager.get_triggers_for_automation("automation_1")
        assert len(triggers) == 2
        assert all(t.automation_id == "automation_1" for t in triggers)

    def test_file_added_trigger_detection(self, tmp_path):
        """Test detecting file added to watched directory."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        manager.register_automation("automation_1", callback)

        watch_dir = str(tmp_path / "watch")
        os.makedirs(watch_dir, exist_ok=True)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="file_added",
            automation_id="automation_1",
            config={"watch_path": watch_dir, "previous_files": []},
            enabled=True
        )

        # Check triggers before adding file
        triggered_count, triggered_ids = manager.check_triggers()
        assert triggered_count == 0

        # Add a file to the watched directory
        test_file = os.path.join(watch_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Check triggers after adding file
        triggered_count, triggered_ids = manager.check_triggers()
        assert triggered_count == 1
        assert "trigger_1" in triggered_ids

    def test_new_email_trigger_execution(self, tmp_path):
        """Test NEW_EMAIL trigger execution."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="email_processed")

        manager.register_automation("automation_1", callback)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        triggered_count, triggered_ids = manager.check_triggers()
        assert triggered_count == 1
        assert "trigger_1" in triggered_ids

        # Verify callback was called
        callback.assert_called_once()

    def test_time_based_trigger_execution(self, tmp_path):
        """Test TIME_BASED trigger execution."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="time_task_executed")

        manager.register_automation("automation_1", callback)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="time_based",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        triggered_count, triggered_ids = manager.check_triggers()
        assert triggered_count == 1
        assert "trigger_1" in triggered_ids

        # Verify callback was called
        callback.assert_called_once()

    def test_disabled_trigger_not_executed(self, tmp_path):
        """Test that disabled triggers are not executed."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        manager.register_automation("automation_1", callback)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=False
        )

        # Check triggers
        triggered_count, triggered_ids = manager.check_triggers()
        assert triggered_count == 0

        # Verify callback was not called
        callback.assert_not_called()

    def test_trigger_execution_logging(self, tmp_path):
        """Test that trigger execution is logged."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        manager.register_automation("automation_1", callback)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        manager.check_triggers()

        # Verify execution was logged
        log = manager.get_execution_log()
        assert len(log) == 1
        assert log[0]["trigger_id"] == "trigger_1"
        assert log[0]["automation_id"] == "automation_1"
        assert log[0]["success"] is True
        assert log[0]["result"] == "success"

    def test_trigger_execution_error_logging(self, tmp_path):
        """Test that trigger execution errors are logged."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(side_effect=Exception("Test error"))

        manager.register_automation("automation_1", callback)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        manager.check_triggers()

        # Verify error was logged
        log = manager.get_execution_log()
        assert len(log) == 1
        assert log[0]["trigger_id"] == "trigger_1"
        assert log[0]["success"] is False
        assert "Test error" in log[0]["error"]

    def test_trigger_count_increments(self, tmp_path):
        """Test that trigger count increments."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        manager.register_automation("automation_1", callback)

        trigger = manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        assert trigger.trigger_count == 0

        # First trigger
        manager.check_triggers()
        trigger = manager.get_trigger("trigger_1")
        assert trigger.trigger_count == 1

        # Reset flag and trigger again
        trigger.config["check_flag"] = True
        manager.check_triggers()
        trigger = manager.get_trigger("trigger_1")
        assert trigger.trigger_count == 2

    def test_get_execution_log_for_trigger(self, tmp_path):
        """Test retrieving execution log for a specific trigger."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        manager.register_automation("automation_1", callback)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        manager.create_trigger(
            trigger_id="trigger_2",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        manager.check_triggers()

        # Get log for trigger_1
        log = manager.get_execution_log_for_trigger("trigger_1")
        assert len(log) == 1
        assert log[0]["trigger_id"] == "trigger_1"

    def test_clear_execution_log(self, tmp_path):
        """Test clearing the execution log."""
        manager = TriggerManager(config_dir=str(tmp_path))
        callback = Mock(return_value="success")

        manager.register_automation("automation_1", callback)

        manager.create_trigger(
            trigger_id="trigger_1",
            trigger_type="new_email",
            automation_id="automation_1",
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        manager.check_triggers()
        assert len(manager.get_execution_log()) == 1

        # Clear log
        manager.clear_execution_log()
        assert len(manager.get_execution_log()) == 0


class TestTriggerManagerProperties:
    """Property-based tests for TriggerManager."""

    @given(
        trigger_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs', 'Zs'))).filter(lambda x: x.strip()),
        automation_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs', 'Zs'))).filter(lambda x: x.strip()),
        trigger_type=st.sampled_from(["new_email", "file_added", "time_based"])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_27_trigger_event_monitoring(self, trigger_id, automation_id, trigger_type):
        """
        **Feature: lazy-automation-platform, Property 27: Trigger Event Monitoring**
        
        For any configured trigger (new email, file added, time-based), the system should 
        monitor for the trigger event and execute the associated automation when triggered.
        
        **Validates: Requirements 10.1, 10.2**
        """
        manager = TriggerManager(config_dir="config")
        callback = Mock(return_value="automation_result")

        # Register automation
        manager.register_automation(automation_id, callback)

        # Create trigger with appropriate config
        if trigger_type == "file_added":
            config = {"watch_path": ".", "previous_files": []}
        else:
            config = {"check_flag": True}

        # Create trigger
        trigger = manager.create_trigger(
            trigger_id=trigger_id,
            trigger_type=trigger_type,
            automation_id=automation_id,
            config=config,
            enabled=True
        )

        # Verify trigger was created
        assert trigger.trigger_id == trigger_id
        assert trigger.automation_id == automation_id
        assert trigger.enabled is True

        # Check triggers
        triggered_count, triggered_ids = manager.check_triggers()

        # Verify trigger was detected and executed
        if trigger_type != "file_added":  # file_added requires actual file
            assert triggered_count > 0
            assert trigger_id in triggered_ids

    @given(
        trigger_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs', 'Zs'))).filter(lambda x: x.strip()),
        automation_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs', 'Zs'))).filter(lambda x: x.strip())
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_28_trigger_event_logging(self, trigger_id, automation_id):
        """
        **Feature: lazy-automation-platform, Property 28: Trigger Event Logging**
        
        For any trigger-based automation execution, the system should log the event and 
        result for audit purposes.
        
        **Validates: Requirements 10.3**
        """
        manager = TriggerManager(config_dir="config")
        callback = Mock(return_value="result_data")

        # Register automation
        manager.register_automation(automation_id, callback)

        # Create trigger
        manager.create_trigger(
            trigger_id=trigger_id,
            trigger_type="new_email",
            automation_id=automation_id,
            config={"check_flag": True},
            enabled=True
        )

        # Check triggers
        manager.check_triggers()

        # Verify execution was logged
        log = manager.get_execution_log_for_trigger(trigger_id)
        assert len(log) > 0
        assert log[0]["trigger_id"] == trigger_id
        assert log[0]["automation_id"] == automation_id
        assert "timestamp" in log[0]
        assert "success" in log[0]

    @given(
        trigger_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs', 'Zs'))).filter(lambda x: x.strip()),
        automation_id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs', 'Zs'))).filter(lambda x: x.strip())
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_29_trigger_disabling(self, trigger_id, automation_id):
        """
        **Feature: lazy-automation-platform, Property 29: Trigger Disabling**
        
        For any disabled trigger, the system should stop monitoring for that trigger event.
        
        **Validates: Requirements 10.4**
        """
        manager = TriggerManager(config_dir="config")
        callback = Mock(return_value="success")

        # Register automation
        manager.register_automation(automation_id, callback)

        # Create trigger
        trigger = manager.create_trigger(
            trigger_id=trigger_id,
            trigger_type="new_email",
            automation_id=automation_id,
            config={"check_flag": True},
            enabled=True
        )

        # Verify trigger is enabled
        assert trigger.enabled is True

        # Disable trigger
        manager.disable_trigger(trigger_id)

        # Verify trigger is disabled
        trigger = manager.get_trigger(trigger_id)
        assert trigger.enabled is False

        # Check triggers - should not execute
        triggered_count, triggered_ids = manager.check_triggers()
        assert trigger_id not in triggered_ids

        # Verify callback was not called
        callback.assert_not_called()

"""Tests for the BackupManager class."""

import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings

from src.backup_manager import BackupManager
from src.data_models import AutomationBackup


@pytest.fixture
def temp_backup_dir():
    """Create a temporary directory for backups."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_files_dir():
    """Create a temporary directory with test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def backup_manager(temp_backup_dir):
    """Create a BackupManager instance with temporary directory."""
    return BackupManager(backup_root_dir=temp_backup_dir)


class TestBackupManagerCreation:
    """Tests for backup creation."""

    def test_create_backup_single_file(self, backup_manager, temp_files_dir):
        """Test creating a backup of a single file."""
        # Create a test file
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")

        # Create backup
        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_file]
        )

        assert success is True
        assert backup is not None
        assert backup.automation_id == "auto_1"
        assert len(backup.affected_files) == 1
        assert backup.can_rollback is True

    def test_create_backup_multiple_files(self, backup_manager, temp_files_dir):
        """Test creating a backup of multiple files."""
        # Create test files
        test_files = []
        for i in range(3):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")
            test_files.append(test_file)

        # Create backup
        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=test_files
        )

        assert success is True
        assert backup is not None
        assert len(backup.affected_files) == 3

    def test_create_backup_directory(self, backup_manager, temp_files_dir):
        """Test creating a backup of a directory."""
        # Create a test directory with files
        test_dir = os.path.join(temp_files_dir, "test_dir")
        os.makedirs(test_dir)
        for i in range(2):
            test_file = os.path.join(test_dir, f"file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

        # Create backup
        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_dir]
        )

        assert success is True
        assert backup is not None

    def test_create_backup_nonexistent_file(self, backup_manager):
        """Test that creating a backup of nonexistent file fails."""
        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=["/nonexistent/file.txt"]
        )

        assert success is False
        assert backup is None
        assert "does not exist" in message

    def test_create_backup_empty_files_list(self, backup_manager):
        """Test that creating a backup with empty files list fails."""
        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[]
        )

        assert success is False
        assert backup is None

    def test_create_backup_invalid_automation_id(self, backup_manager, temp_files_dir):
        """Test that creating a backup with invalid automation_id fails."""
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")

        success, message, backup = backup_manager.create_backup(
            automation_id="",
            affected_files=[test_file]
        )

        assert success is False
        assert backup is None


class TestBackupManagerRestoration:
    """Tests for backup restoration."""

    def test_restore_backup_single_file(self, backup_manager, temp_files_dir):
        """Test restoring a backup of a single file."""
        # Create and backup a file
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("original content")

        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_file]
        )
        assert success is True

        # Modify the file
        with open(test_file, 'w') as f:
            f.write("modified content")

        # Restore backup
        restore_success, restore_message = backup_manager.restore_backup(backup.backup_id)

        assert restore_success is True
        with open(test_file, 'r') as f:
            content = f.read()
        assert content == "original content"

    def test_restore_backup_multiple_files(self, backup_manager, temp_files_dir):
        """Test restoring a backup of multiple files."""
        # Create and backup multiple files
        test_files = []
        for i in range(3):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"original {i}")
            test_files.append(test_file)

        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=test_files
        )
        assert success is True

        # Modify files
        for test_file in test_files:
            with open(test_file, 'w') as f:
                f.write("modified")

        # Restore backup
        restore_success, restore_message = backup_manager.restore_backup(backup.backup_id)

        assert restore_success is True
        for i, test_file in enumerate(test_files):
            with open(test_file, 'r') as f:
                content = f.read()
            assert content == f"original {i}"

    def test_restore_nonexistent_backup(self, backup_manager):
        """Test that restoring a nonexistent backup fails."""
        success, message = backup_manager.restore_backup("nonexistent_backup_id")

        assert success is False
        assert "not found" in message

    def test_restore_backup_deleted_file(self, backup_manager, temp_files_dir):
        """Test restoring a backup when the original file was deleted."""
        # Create and backup a file
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("original content")

        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_file]
        )
        assert success is True

        # Delete the file
        os.remove(test_file)
        assert not os.path.exists(test_file)

        # Restore backup
        restore_success, restore_message = backup_manager.restore_backup(backup.backup_id)

        assert restore_success is True
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            content = f.read()
        assert content == "original content"


class TestBackupManagerListing:
    """Tests for listing and retrieving backups."""

    def test_list_all_backups(self, backup_manager, temp_files_dir):
        """Test listing all backups."""
        # Create multiple backups
        for i in range(3):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

            backup_manager.create_backup(
                automation_id=f"auto_{i}",
                affected_files=[test_file]
            )

        backups = backup_manager.list_backups()
        assert len(backups) == 3

    def test_list_backups_by_automation_id(self, backup_manager, temp_files_dir):
        """Test listing backups filtered by automation_id."""
        # Create backups for different automations
        for i in range(3):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

            backup_manager.create_backup(
                automation_id="auto_1" if i < 2 else "auto_2",
                affected_files=[test_file]
            )

        backups = backup_manager.list_backups(automation_id="auto_1")
        assert len(backups) == 2
        assert all(b.automation_id == "auto_1" for b in backups)

    def test_get_backup(self, backup_manager, temp_files_dir):
        """Test getting a specific backup."""
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")

        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_file]
        )

        retrieved_backup = backup_manager.get_backup(backup.backup_id)
        assert retrieved_backup is not None
        assert retrieved_backup.backup_id == backup.backup_id
        assert retrieved_backup.automation_id == "auto_1"


class TestBackupManagerDeletion:
    """Tests for backup deletion."""

    def test_delete_backup(self, backup_manager, temp_files_dir):
        """Test deleting a backup."""
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")

        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_file]
        )
        assert success is True

        # Delete backup
        delete_success, delete_message = backup_manager.delete_backup(backup.backup_id)

        assert delete_success is True
        assert backup_manager.get_backup(backup.backup_id) is None

    def test_delete_nonexistent_backup(self, backup_manager):
        """Test deleting a nonexistent backup."""
        success, message = backup_manager.delete_backup("nonexistent_backup_id")

        assert success is False
        assert "not found" in message


class TestBackupManagerCleanup:
    """Tests for backup cleanup."""

    def test_cleanup_old_backups(self, backup_manager, temp_files_dir):
        """Test cleaning up old backups."""
        # Create multiple backups
        for i in range(15):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

            backup_manager.create_backup(
                automation_id="auto_1",
                affected_files=[test_file]
            )

        # Cleanup, keeping only 10
        deleted_count, message = backup_manager.cleanup_old_backups(max_backups=10)

        assert deleted_count == 5
        remaining_backups = backup_manager.list_backups()
        assert len(remaining_backups) == 10


class TestBackupManagerUndoHistory:
    """Tests for undo history."""

    def test_get_undo_history(self, backup_manager, temp_files_dir):
        """Test getting undo history."""
        # Create multiple backups
        for i in range(5):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

            backup_manager.create_backup(
                automation_id="auto_1",
                affected_files=[test_file]
            )

        history = backup_manager.get_undo_history(limit=3)
        assert len(history) == 3
        # Most recent should be first
        assert history[0].timestamp >= history[1].timestamp

    def test_get_undo_history_limit(self, backup_manager, temp_files_dir):
        """Test undo history respects limit."""
        # Create multiple backups
        for i in range(10):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

            backup_manager.create_backup(
                automation_id="auto_1",
                affected_files=[test_file]
            )

        history = backup_manager.get_undo_history(limit=5)
        assert len(history) == 5


class TestBackupManagerRollbackLogging:
    """Tests for rollback logging."""

    def test_log_rollback(self, backup_manager, temp_files_dir):
        """Test logging a rollback action."""
        test_file = os.path.join(temp_files_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("content")

        success, message, backup = backup_manager.create_backup(
            automation_id="auto_1",
            affected_files=[test_file]
        )

        # Log rollback
        log_success, log_message = backup_manager.log_rollback(backup.backup_id, success=True)

        assert log_success is True

    def test_get_rollback_history(self, backup_manager, temp_files_dir):
        """Test getting rollback history."""
        # Create and rollback multiple backups
        for i in range(3):
            test_file = os.path.join(temp_files_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")

            success, message, backup = backup_manager.create_backup(
                automation_id="auto_1",
                affected_files=[test_file]
            )

            backup_manager.log_rollback(backup.backup_id, success=True)

        history = backup_manager.get_rollback_history()
        assert len(history) == 3


# Property-Based Tests

@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    num_files=st.integers(min_value=1, max_value=5)
)
@settings(deadline=None)
def test_property_backup_creation(automation_id, num_files):
    """
    **Feature: lazy-automation-platform, Property 38: Backup Creation**
    
    *For any* automation execution, the system should create a backup of affected files before making changes.
    **Validates: Requirements 13.1**
    """
    with tempfile.TemporaryDirectory() as temp_backup_dir:
        backup_manager = BackupManager(backup_root_dir=temp_backup_dir)
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            test_files = []
            for i in range(num_files):
                test_file = os.path.join(temp_dir, f"test_{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"content {i}")
                test_files.append(test_file)

            # Create backup
            success, message, backup = backup_manager.create_backup(
                automation_id=automation_id,
                affected_files=test_files
            )

            # Property: backup should be created successfully
            assert success is True
            assert backup is not None
            assert backup.automation_id == automation_id
            assert len(backup.affected_files) == num_files
            assert backup.can_rollback is True
            assert os.path.exists(backup.backup_location)


@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    num_files=st.integers(min_value=1, max_value=3)
)
def test_property_undo_restoration(automation_id, num_files):
    """
    **Feature: lazy-automation-platform, Property 39: Undo Restoration**
    
    *For any* undo request, the system should restore files from backup and remove any created files.
    **Validates: Requirements 13.2**
    """
    with tempfile.TemporaryDirectory() as temp_backup_dir:
        backup_manager = BackupManager(backup_root_dir=temp_backup_dir)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and backup files with original content
            test_files = []
            original_contents = {}
            for i in range(num_files):
                test_file = os.path.join(temp_dir, f"test_{i}.txt")
                original_content = f"original {i}"
                with open(test_file, 'w') as f:
                    f.write(original_content)
                test_files.append(test_file)
                original_contents[test_file] = original_content

            # Create backup
            success, message, backup = backup_manager.create_backup(
                automation_id=automation_id,
                affected_files=test_files
            )
            assert success is True

            # Modify files (simulate automation changes)
            for test_file in test_files:
                with open(test_file, 'w') as f:
                    f.write("modified content")

            # Restore backup
            restore_success, restore_message = backup_manager.restore_backup(backup.backup_id)

            # Property: restoration should succeed and restore original content
            assert restore_success is True
            for test_file in test_files:
                with open(test_file, 'r') as f:
                    content = f.read()
                assert content == original_contents[test_file]


@given(
    automation_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    num_files=st.integers(min_value=1, max_value=3),
    success_flag=st.booleans()
)
def test_property_rollback_logging(automation_id, num_files, success_flag):
    """
    **Feature: lazy-automation-platform, Property 40: Rollback Logging**
    
    *For any* rollback execution, the system should log the rollback action with timestamp and affected files.
    **Validates: Requirements 13.3**
    """
    with tempfile.TemporaryDirectory() as temp_backup_dir:
        backup_manager = BackupManager(backup_root_dir=temp_backup_dir)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = []
            for i in range(num_files):
                test_file = os.path.join(temp_dir, f"test_{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"content {i}")
                test_files.append(test_file)

            # Create backup
            success, message, backup = backup_manager.create_backup(
                automation_id=automation_id,
                affected_files=test_files
            )
            assert success is True

            # Log rollback
            log_success, log_message = backup_manager.log_rollback(
                backup_id=backup.backup_id,
                success=success_flag
            )

            # Property: rollback logging should succeed
            assert log_success is True

            # Property: rollback history should contain the logged entry
            history = backup_manager.get_rollback_history()
            assert len(history) > 0

            # Property: the most recent entry should match our rollback
            latest_entry = history[-1]
            assert latest_entry["backup_id"] == backup.backup_id
            assert latest_entry["automation_id"] == automation_id
            assert latest_entry["success"] == success_flag
            assert len(latest_entry["affected_files"]) == num_files

            # Property: rollback log entry should have timestamp
            assert "timestamp" in latest_entry
            assert latest_entry["timestamp"] is not None
            assert len(latest_entry["timestamp"]) > 0

            # Property: affected files in log should match original affected files
            assert set(latest_entry["affected_files"]) == set(test_files)


@given(
    num_backups=st.integers(min_value=1, max_value=15),
    limit=st.integers(min_value=1, max_value=10)
)
def test_property_undo_history_display(num_backups, limit):
    """
    **Feature: lazy-automation-platform, Property 41: Undo History Display**
    
    *For any* undo history request, the system should display a list of recent automations that can be undone.
    **Validates: Requirements 13.4**
    """
    with tempfile.TemporaryDirectory() as temp_backup_dir:
        backup_manager = BackupManager(backup_root_dir=temp_backup_dir)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple backups
            created_backups = []
            for i in range(num_backups):
                test_file = os.path.join(temp_dir, f"test_{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"content {i}")

                success, message, backup = backup_manager.create_backup(
                    automation_id=f"auto_{i}",
                    affected_files=[test_file]
                )
                
                if success:
                    created_backups.append(backup)

            # Get undo history with limit
            history = backup_manager.get_undo_history(limit=limit)

            # Property: undo history should return a list
            assert isinstance(history, list)

            # Property: undo history should not exceed the limit
            assert len(history) <= limit

            # Property: undo history should not exceed the number of created backups
            assert len(history) <= len(created_backups)

            # Property: all items in undo history should be AutomationBackup objects
            for item in history:
                assert isinstance(item, AutomationBackup)

            # Property: all items in undo history should be rollbackable
            for item in history:
                assert item.can_rollback is True

            # Property: undo history should be sorted by timestamp (most recent first)
            if len(history) > 1:
                for i in range(len(history) - 1):
                    assert history[i].timestamp >= history[i + 1].timestamp

            # Property: each backup in undo history should have valid metadata
            for item in history:
                assert item.backup_id is not None
                assert len(item.backup_id) > 0
                assert item.automation_id is not None
                assert len(item.automation_id) > 0
                assert item.affected_files is not None
                assert len(item.affected_files) > 0
                assert item.backup_location is not None
                assert len(item.backup_location) > 0
                assert item.timestamp is not None
                assert len(item.timestamp) > 0

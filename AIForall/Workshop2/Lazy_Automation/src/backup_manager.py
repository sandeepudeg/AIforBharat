"""Backup and undo management for the Lazy Automation Platform."""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from uuid import uuid4

from src.data_models import AutomationBackup, ValidationError
from src.file_service import FileService


class BackupManager:
    """Manages backup creation, restoration, and undo operations."""

    def __init__(self, backup_root_dir: str = "data/backups"):
        """
        Initialize the BackupManager.

        Args:
            backup_root_dir: Root directory for storing backups
        """
        self.backup_root_dir = backup_root_dir
        self.backup_metadata_file = os.path.join(backup_root_dir, "backups.json")
        self.backups: Dict[str, AutomationBackup] = {}

        # Create backup directory if it doesn't exist
        os.makedirs(backup_root_dir, exist_ok=True)

        # Load existing backups
        self._load_backups()

    def _load_backups(self) -> None:
        """Load backup metadata from storage."""
        if os.path.exists(self.backup_metadata_file):
            try:
                with open(self.backup_metadata_file, 'r') as f:
                    data = json.load(f)
                    for backup_id, backup_data in data.items():
                        self.backups[backup_id] = AutomationBackup.from_json(
                            json.dumps(backup_data)
                        )
            except (json.JSONDecodeError, ValidationError):
                # If metadata is corrupted, start fresh
                self.backups = {}

    def _save_backups(self) -> None:
        """Save backup metadata to storage."""
        backup_data = {}
        for backup_id, backup in self.backups.items():
            backup_data[backup_id] = json.loads(backup.to_json())

        with open(self.backup_metadata_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

    def create_backup(
        self,
        automation_id: str,
        affected_files: List[str]
    ) -> Tuple[bool, str, Optional[AutomationBackup]]:
        """
        Create a backup of affected files before automation execution.

        Args:
            automation_id: ID of the automation task
            affected_files: List of file paths to backup

        Returns:
            Tuple of (success, message, backup_object)
            If successful, backup_object contains the created backup
        """
        if not automation_id or not isinstance(automation_id, str):
            return False, "automation_id must be a non-empty string", None

        if not isinstance(affected_files, list):
            return False, "affected_files must be a list", None

        if len(affected_files) == 0:
            return False, "affected_files cannot be empty", None

        # Validate all files exist
        for file_path in affected_files:
            if not os.path.exists(file_path):
                return False, f"File does not exist: {file_path}", None

        # Create backup directory for this backup
        backup_id = str(uuid4())
        backup_dir = os.path.join(self.backup_root_dir, backup_id)

        try:
            os.makedirs(backup_dir, exist_ok=True)

            # Copy all affected files to backup directory
            for file_path in affected_files:
                if os.path.isfile(file_path):
                    # Use just the filename to preserve in backup
                    file_name = os.path.basename(file_path)
                    backup_file_path = os.path.join(backup_dir, file_name)
                    shutil.copy2(file_path, backup_file_path)
                elif os.path.isdir(file_path):
                    # Backup entire directory with its name
                    dir_name = os.path.basename(file_path)
                    backup_dir_path = os.path.join(backup_dir, dir_name)
                    shutil.copytree(file_path, backup_dir_path)

            # Create backup metadata
            backup = AutomationBackup(
                backup_id=backup_id,
                automation_id=automation_id,
                affected_files=affected_files,
                backup_location=backup_dir,
                can_rollback=True
            )

            # Store backup metadata
            self.backups[backup_id] = backup
            self._save_backups()

            return True, f"Backup created successfully: {backup_id}", backup

        except Exception as e:
            # Clean up partial backup
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            return False, f"Failed to create backup: {str(e)}", None

    def restore_backup(self, backup_id: str) -> Tuple[bool, str]:
        """
        Restore files from a backup.

        Args:
            backup_id: ID of the backup to restore

        Returns:
            Tuple of (success, message)
        """
        if backup_id not in self.backups:
            return False, f"Backup not found: {backup_id}"

        backup = self.backups[backup_id]

        if not backup.can_rollback:
            return False, "This backup cannot be rolled back"

        backup_dir = backup.backup_location

        if not os.path.exists(backup_dir):
            return False, f"Backup directory not found: {backup_dir}"

        try:
            # Restore each affected file
            for original_file_path in backup.affected_files:
                file_name = os.path.basename(original_file_path)
                backup_file_path = os.path.join(backup_dir, file_name)

                if os.path.exists(backup_file_path):
                    # Remove current file/directory if it exists
                    if os.path.exists(original_file_path):
                        if os.path.isfile(original_file_path):
                            os.remove(original_file_path)
                        elif os.path.isdir(original_file_path):
                            shutil.rmtree(original_file_path)

                    # Restore from backup
                    if os.path.isfile(backup_file_path):
                        # Ensure parent directory exists
                        parent_dir = os.path.dirname(original_file_path)
                        os.makedirs(parent_dir, exist_ok=True)
                        shutil.copy2(backup_file_path, original_file_path)
                    elif os.path.isdir(backup_file_path):
                        shutil.copytree(backup_file_path, original_file_path)

            return True, f"Backup restored successfully: {backup_id}"

        except Exception as e:
            return False, f"Failed to restore backup: {str(e)}"

    def get_backup(self, backup_id: str) -> Optional[AutomationBackup]:
        """
        Get backup metadata by ID.

        Args:
            backup_id: ID of the backup

        Returns:
            AutomationBackup object or None if not found
        """
        return self.backups.get(backup_id)

    def list_backups(self, automation_id: Optional[str] = None) -> List[AutomationBackup]:
        """
        List all backups, optionally filtered by automation_id.

        Args:
            automation_id: Optional automation ID to filter by

        Returns:
            List of AutomationBackup objects
        """
        backups = list(self.backups.values())

        if automation_id:
            backups = [b for b in backups if b.automation_id == automation_id]

        # Sort by timestamp (most recent first)
        backups.sort(key=lambda b: b.timestamp, reverse=True)

        return backups

    def delete_backup(self, backup_id: str) -> Tuple[bool, str]:
        """
        Delete a backup and its associated files.

        Args:
            backup_id: ID of the backup to delete

        Returns:
            Tuple of (success, message)
        """
        if backup_id not in self.backups:
            return False, f"Backup not found: {backup_id}"

        backup = self.backups[backup_id]
        backup_dir = backup.backup_location

        try:
            # Remove backup directory
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

            # Remove from metadata
            del self.backups[backup_id]
            self._save_backups()

            return True, f"Backup deleted successfully: {backup_id}"

        except Exception as e:
            return False, f"Failed to delete backup: {str(e)}"

    def cleanup_old_backups(self, max_backups: int = 10) -> Tuple[int, str]:
        """
        Clean up old backups, keeping only the most recent ones.

        Args:
            max_backups: Maximum number of backups to keep

        Returns:
            Tuple of (deleted_count, message)
        """
        if max_backups <= 0:
            return 0, "max_backups must be greater than 0"

        # Sort backups by timestamp (oldest first)
        sorted_backups = sorted(
            self.backups.items(),
            key=lambda x: x[1].timestamp
        )

        deleted_count = 0
        backups_to_delete = sorted_backups[:-max_backups]

        for backup_id, _ in backups_to_delete:
            success, _ = self.delete_backup(backup_id)
            if success:
                deleted_count += 1

        return deleted_count, f"Deleted {deleted_count} old backups"

    def get_undo_history(self, limit: int = 20) -> List[AutomationBackup]:
        """
        Get undo history (list of recent backups that can be undone).

        Args:
            limit: Maximum number of backups to return

        Returns:
            List of AutomationBackup objects sorted by timestamp (most recent first)
        """
        if limit <= 0:
            return []

        # Get all backups sorted by timestamp (most recent first)
        all_backups = sorted(
            self.backups.values(),
            key=lambda b: b.timestamp,
            reverse=True
        )

        # Filter to only rollbackable backups
        rollbackable = [b for b in all_backups if b.can_rollback]

        return rollbackable[:limit]

    def log_rollback(self, backup_id: str, success: bool) -> Tuple[bool, str]:
        """
        Log a rollback action.

        Args:
            backup_id: ID of the backup that was rolled back
            success: Whether the rollback was successful

        Returns:
            Tuple of (success, message)
        """
        if backup_id not in self.backups:
            return False, f"Backup not found: {backup_id}"

        backup = self.backups[backup_id]

        # Create rollback log entry
        log_entry = {
            "backup_id": backup_id,
            "automation_id": backup.automation_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "affected_files": backup.affected_files
        }

        # Append to rollback log file
        rollback_log_file = os.path.join(self.backup_root_dir, "rollback_log.json")

        try:
            # Load existing log
            if os.path.exists(rollback_log_file):
                with open(rollback_log_file, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = []

            # Append new entry
            log_data.append(log_entry)

            # Save updated log
            with open(rollback_log_file, 'w') as f:
                json.dump(log_data, f, indent=2)

            return True, "Rollback logged successfully"

        except Exception as e:
            return False, f"Failed to log rollback: {str(e)}"

    def get_rollback_history(self) -> List[Dict]:
        """
        Get rollback history.

        Returns:
            List of rollback log entries
        """
        rollback_log_file = os.path.join(self.backup_root_dir, "rollback_log.json")

        if not os.path.exists(rollback_log_file):
            return []

        try:
            with open(rollback_log_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

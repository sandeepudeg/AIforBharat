"""Lazy Automation Platform - Core modules."""

from src.config_manager import ConfigManager
from src.backup_manager import BackupManager
from src.data_models import (
    AutomationConfig,
    FileOperationResult,
    EmailSummary,
    ClipboardItem,
    ScheduledTask,
    WorkflowChain,
    CustomRule,
    AutomationBackup,
)

__all__ = [
    "ConfigManager",
    "BackupManager",
    "AutomationConfig",
    "FileOperationResult",
    "EmailSummary",
    "ClipboardItem",
    "ScheduledTask",
    "WorkflowChain",
    "CustomRule",
    "AutomationBackup",
]

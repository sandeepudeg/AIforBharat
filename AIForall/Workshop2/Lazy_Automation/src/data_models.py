"""Core data models for the Lazy Automation Platform."""

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


@dataclass
class AutomationConfig:
    """Configuration for an automation task."""

    task_name: str
    enabled: bool
    options: Dict[str, Any] = field(default_factory=dict)
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate the configuration after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the AutomationConfig."""
        if not isinstance(self.task_name, str) or not self.task_name.strip():
            raise ValidationError("task_name must be a non-empty string")
        if not isinstance(self.enabled, bool):
            raise ValidationError("enabled must be a boolean")
        if not isinstance(self.options, dict):
            raise ValidationError("options must be a dictionary")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "AutomationConfig":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class FileOperationResult:
    """Result of a file operation."""

    success: bool
    processed_count: int
    error_count: int
    details: List[Dict[str, Any]] = field(default_factory=list)
    download_path: Optional[str] = None

    def __post_init__(self):
        """Validate the result after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the FileOperationResult."""
        if not isinstance(self.success, bool):
            raise ValidationError("success must be a boolean")
        if not isinstance(self.processed_count, int) or self.processed_count < 0:
            raise ValidationError("processed_count must be a non-negative integer")
        if not isinstance(self.error_count, int) or self.error_count < 0:
            raise ValidationError("error_count must be a non-negative integer")
        if not isinstance(self.details, list):
            raise ValidationError("details must be a list")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "FileOperationResult":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class EmailSummary:
    """Summary of an email."""

    sender: str
    subject: str
    summary: str
    original_length: int
    summary_length: int

    def __post_init__(self):
        """Validate the summary after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the EmailSummary."""
        if not isinstance(self.sender, str) or not self.sender.strip():
            raise ValidationError("sender must be a non-empty string")
        if not isinstance(self.subject, str):
            raise ValidationError("subject must be a string")
        if not isinstance(self.summary, str):
            raise ValidationError("summary must be a string")
        if not isinstance(self.original_length, int) or self.original_length < 0:
            raise ValidationError("original_length must be a non-negative integer")
        if not isinstance(self.summary_length, int) or self.summary_length < 0:
            raise ValidationError("summary_length must be a non-negative integer")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "EmailSummary":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class ClipboardItem:
    """Item in clipboard history."""

    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source_task: str = ""
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate the item after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the ClipboardItem."""
        if not isinstance(self.content, str):
            raise ValidationError("content must be a string")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValidationError("timestamp must be a non-empty string")
        if not isinstance(self.source_task, str):
            raise ValidationError("source_task must be a string")
        if not isinstance(self.tags, list):
            raise ValidationError("tags must be a list")
        if not all(isinstance(tag, str) for tag in self.tags):
            raise ValidationError("all tags must be strings")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "ClipboardItem":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class ScheduledTask:
    """Scheduled automation task."""

    task_id: str
    task_name: str
    schedule: str  # cron format or interval
    enabled: bool
    execution_count: int = 0
    last_execution: Optional[str] = None
    next_execution: str = ""

    def __post_init__(self):
        """Validate the task after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the ScheduledTask."""
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValidationError("task_id must be a non-empty string")
        if not isinstance(self.task_name, str) or not self.task_name.strip():
            raise ValidationError("task_name must be a non-empty string")
        if not isinstance(self.schedule, str) or not self.schedule.strip():
            raise ValidationError("schedule must be a non-empty string")
        if not isinstance(self.enabled, bool):
            raise ValidationError("enabled must be a boolean")
        if not isinstance(self.execution_count, int) or self.execution_count < 0:
            raise ValidationError("execution_count must be a non-negative integer")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "ScheduledTask":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class WorkflowChain:
    """Chain of automation tasks."""

    chain_id: str
    name: str
    tasks: List[str]  # ordered list of task IDs
    enabled: bool
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_executed: Optional[str] = None

    def __post_init__(self):
        """Validate the chain after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the WorkflowChain."""
        if not isinstance(self.chain_id, str) or not self.chain_id.strip():
            raise ValidationError("chain_id must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("name must be a non-empty string")
        if not isinstance(self.tasks, list):
            raise ValidationError("tasks must be a list")
        if not all(isinstance(task, str) for task in self.tasks):
            raise ValidationError("all tasks must be strings")
        if not isinstance(self.enabled, bool):
            raise ValidationError("enabled must be a boolean")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "WorkflowChain":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class CustomRule:
    """Custom automation rule."""

    rule_id: str
    name: str
    conditions: Dict[str, Any]  # condition definitions
    actions: List[Dict[str, Any]]  # action definitions
    enabled: bool
    execution_count: int = 0

    def __post_init__(self):
        """Validate the rule after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the CustomRule."""
        if not isinstance(self.rule_id, str) or not self.rule_id.strip():
            raise ValidationError("rule_id must be a non-empty string")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("name must be a non-empty string")
        if not isinstance(self.conditions, dict):
            raise ValidationError("conditions must be a dictionary")
        if not isinstance(self.actions, list):
            raise ValidationError("actions must be a list")
        if not all(isinstance(action, dict) for action in self.actions):
            raise ValidationError("all actions must be dictionaries")
        if not isinstance(self.enabled, bool):
            raise ValidationError("enabled must be a boolean")
        if not isinstance(self.execution_count, int) or self.execution_count < 0:
            raise ValidationError("execution_count must be a non-negative integer")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "CustomRule":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class AutomationBackup:
    """Backup of automation execution."""

    backup_id: str
    automation_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    affected_files: List[str] = field(default_factory=list)
    backup_location: str = ""
    can_rollback: bool = True

    def __post_init__(self):
        """Validate the backup after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the AutomationBackup."""
        if not isinstance(self.backup_id, str) or not self.backup_id.strip():
            raise ValidationError("backup_id must be a non-empty string")
        if not isinstance(self.automation_id, str) or not self.automation_id.strip():
            raise ValidationError("automation_id must be a non-empty string")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValidationError("timestamp must be a non-empty string")
        if not isinstance(self.affected_files, list):
            raise ValidationError("affected_files must be a list")
        if not all(isinstance(f, str) for f in self.affected_files):
            raise ValidationError("all affected_files must be strings")
        if not isinstance(self.backup_location, str):
            raise ValidationError("backup_location must be a string")
        if not isinstance(self.can_rollback, bool):
            raise ValidationError("can_rollback must be a boolean")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "AutomationBackup":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class ExecutionRecord:
    """Record of an automation execution."""

    execution_id: str
    automation_id: str
    automation_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    duration_seconds: float = 0.0
    items_processed: int = 0
    errors: List[str] = field(default_factory=list)
    time_saved_minutes: float = 0.0

    def __post_init__(self):
        """Validate the record after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the ExecutionRecord."""
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValidationError("execution_id must be a non-empty string")
        if not isinstance(self.automation_id, str) or not self.automation_id.strip():
            raise ValidationError("automation_id must be a non-empty string")
        if not isinstance(self.automation_name, str) or not self.automation_name.strip():
            raise ValidationError("automation_name must be a non-empty string")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValidationError("timestamp must be a non-empty string")
        if not isinstance(self.success, bool):
            raise ValidationError("success must be a boolean")
        if not isinstance(self.duration_seconds, (int, float)) or self.duration_seconds < 0:
            raise ValidationError("duration_seconds must be a non-negative number")
        if not isinstance(self.items_processed, int) or self.items_processed < 0:
            raise ValidationError("items_processed must be a non-negative integer")
        if not isinstance(self.errors, list):
            raise ValidationError("errors must be a list")
        if not all(isinstance(e, str) for e in self.errors):
            raise ValidationError("all errors must be strings")
        if not isinstance(self.time_saved_minutes, (int, float)) or self.time_saved_minutes < 0:
            raise ValidationError("time_saved_minutes must be a non-negative number")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> "ExecutionRecord":
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)

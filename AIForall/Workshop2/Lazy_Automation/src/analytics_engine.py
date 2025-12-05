"""Analytics engine for tracking automation usage and calculating statistics."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from src.data_models import ExecutionRecord, ValidationError


class AnalyticsEngine:
    """Tracks automation execution and calculates usage statistics."""

    def __init__(self, analytics_dir: str = "data"):
        """
        Initialize the AnalyticsEngine.

        Args:
            analytics_dir: Directory where analytics data is stored
        """
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        self.records_file = self.analytics_dir / "execution_records.json"
        self._records: List[ExecutionRecord] = []
        self._load_records()

    def _load_records(self) -> None:
        """Load execution records from storage."""
        if self.records_file.exists():
            try:
                with open(self.records_file, "r") as f:
                    data = json.load(f)
                    self._records = [ExecutionRecord.from_json(json.dumps(record)) for record in data]
            except (json.JSONDecodeError, IOError, ValidationError):
                self._records = []
        else:
            self._records = []

    def _save_records(self) -> None:
        """Save execution records to storage."""
        records_data = [json.loads(record.to_json()) for record in self._records]
        with open(self.records_file, "w") as f:
            json.dump(records_data, f, indent=2)

    def record_execution(
        self,
        execution_id: str,
        automation_id: str,
        automation_name: str,
        success: bool = True,
        duration_seconds: float = 0.0,
        items_processed: int = 0,
        errors: Optional[List[str]] = None,
        time_saved_minutes: float = 0.0,
    ) -> ExecutionRecord:
        """
        Record an automation execution.

        Args:
            execution_id: Unique execution identifier
            automation_id: Automation task identifier
            automation_name: Human-readable automation name
            success: Whether execution was successful
            duration_seconds: Execution duration in seconds
            items_processed: Number of items processed
            errors: List of error messages if any
            time_saved_minutes: Estimated time saved in minutes

        Returns:
            ExecutionRecord created
        """
        if errors is None:
            errors = []

        record = ExecutionRecord(
            execution_id=execution_id,
            automation_id=automation_id,
            automation_name=automation_name,
            success=success,
            duration_seconds=duration_seconds,
            items_processed=items_processed,
            errors=errors,
            time_saved_minutes=time_saved_minutes,
        )

        self._records.append(record)
        self._save_records()
        return record

    def get_execution_history(
        self, automation_id: Optional[str] = None, limit: int = 100
    ) -> List[ExecutionRecord]:
        """
        Get execution history.

        Args:
            automation_id: Filter by automation ID (None for all)
            limit: Maximum number of records to return

        Returns:
            List of execution records
        """
        records = self._records
        if automation_id:
            records = [r for r in records if r.automation_id == automation_id]

        # Sort by timestamp descending (most recent first)
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return records[:limit]

    def calculate_time_saved(self, automation_id: Optional[str] = None) -> float:
        """
        Calculate total time saved.

        Args:
            automation_id: Filter by automation ID (None for all)

        Returns:
            Total time saved in minutes
        """
        records = self._records
        if automation_id:
            records = [r for r in records if r.automation_id == automation_id]

        return sum(r.time_saved_minutes for r in records if r.success)

    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics across all automations.

        Returns:
            Dictionary containing usage statistics
        """
        if not self._records:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "success_rate": 0.0,
                "total_items_processed": 0,
                "total_time_saved_minutes": 0.0,
                "average_duration_seconds": 0.0,
                "automations": {},
            }

        total_executions = len(self._records)
        successful = sum(1 for r in self._records if r.success)
        failed = total_executions - successful
        success_rate = (successful / total_executions * 100) if total_executions > 0 else 0.0
        total_items = sum(r.items_processed for r in self._records)
        total_time_saved = sum(r.time_saved_minutes for r in self._records if r.success)
        avg_duration = (
            sum(r.duration_seconds for r in self._records) / total_executions
            if total_executions > 0
            else 0.0
        )

        # Per-automation statistics
        automation_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "executions": 0,
                "successful": 0,
                "failed": 0,
                "items_processed": 0,
                "time_saved_minutes": 0.0,
            }
        )

        for record in self._records:
            auto_id = record.automation_id
            automation_stats[auto_id]["executions"] += 1
            if record.success:
                automation_stats[auto_id]["successful"] += 1
            else:
                automation_stats[auto_id]["failed"] += 1
            automation_stats[auto_id]["items_processed"] += record.items_processed
            automation_stats[auto_id]["time_saved_minutes"] += record.time_saved_minutes

        return {
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": round(success_rate, 2),
            "total_items_processed": total_items,
            "total_time_saved_minutes": round(total_time_saved, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "automations": dict(automation_stats),
        }

    def get_error_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze error trends over a time period.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary containing error trend analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [
            r
            for r in self._records
            if datetime.fromisoformat(r.timestamp) >= cutoff_date
        ]

        if not recent_records:
            return {
                "period_days": days,
                "total_errors": 0,
                "error_rate": 0.0,
                "errors_by_automation": {},
                "most_common_errors": [],
            }

        failed_records = [r for r in recent_records if not r.success]
        total_errors = len(failed_records)
        error_rate = (
            (total_errors / len(recent_records) * 100) if recent_records else 0.0
        )

        # Errors by automation
        errors_by_automation: Dict[str, int] = defaultdict(int)
        all_errors: List[str] = []

        for record in failed_records:
            errors_by_automation[record.automation_id] += 1
            all_errors.extend(record.errors)

        # Most common errors
        error_counts: Dict[str, int] = defaultdict(int)
        for error in all_errors:
            error_counts[error] += 1

        most_common = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "period_days": days,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "errors_by_automation": dict(errors_by_automation),
            "most_common_errors": [{"error": e, "count": c} for e, c in most_common],
        }

    def get_automation_frequency(self, days: int = 30) -> Dict[str, int]:
        """
        Get automation usage frequency over a time period.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary mapping automation IDs to execution counts
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [
            r
            for r in self._records
            if datetime.fromisoformat(r.timestamp) >= cutoff_date
        ]

        frequency: Dict[str, int] = defaultdict(int)
        for record in recent_records:
            frequency[record.automation_id] += 1

        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive dashboard summary.

        Returns:
            Dictionary containing dashboard data
        """
        stats = self.get_usage_statistics()
        errors = self.get_error_trends()
        frequency = self.get_automation_frequency()

        return {
            "timestamp": datetime.now().isoformat(),
            "usage_statistics": stats,
            "error_trends": errors,
            "automation_frequency": frequency,
            "recent_executions": [
                json.loads(r.to_json()) for r in self.get_execution_history(limit=10)
            ],
        }

    def clear_old_records(self, days: int = 90) -> int:
        """
        Clear execution records older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self._records)

        self._records = [
            r
            for r in self._records
            if datetime.fromisoformat(r.timestamp) >= cutoff_date
        ]

        deleted_count = original_count - len(self._records)
        if deleted_count > 0:
            self._save_records()

        return deleted_count

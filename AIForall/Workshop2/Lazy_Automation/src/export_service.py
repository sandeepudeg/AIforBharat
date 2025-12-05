"""Export service for automation results with metadata and sensitive data handling."""

import json
import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import asdict
from src.data_models import (
    FileOperationResult,
    EmailSummary,
    ClipboardItem,
    ExecutionRecord,
    AutomationConfig
)
from src.error_handler import ErrorHandler


class ExportService:
    """Handles exporting automation results with metadata and sensitive data exclusion."""

    # Sensitive keywords that should be excluded from exports
    SENSITIVE_KEYWORDS = [
        'password', 'passwd', 'pwd',
        'token', 'auth',
        'key', 'api_key', 'apikey',
        'secret', 'credential',
        'email', 'phone',
        'ssn', 'social_security',
        'credit_card', 'card_number'
    ]

    def __init__(self, export_dir: str = "data/exports"):
        """
        Initialize the ExportService.

        Args:
            export_dir: Directory where exports are saved
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_results_json(
        self,
        results: Any,
        automation_name: str,
        config: Optional[AutomationConfig] = None,
        exclude_sensitive: bool = True
    ) -> str:
        """
        Export results as JSON with metadata.

        Args:
            results: Results to export (can be dict, list, or dataclass)
            automation_name: Name of the automation task
            config: Optional automation configuration to include as metadata
            exclude_sensitive: Whether to exclude sensitive data

        Returns:
            Path to the exported file
        """
        # Convert dataclass to dict if needed
        if hasattr(results, '__dataclass_fields__'):
            results_dict = asdict(results)
        elif isinstance(results, dict):
            results_dict = results
        elif isinstance(results, list):
            results_dict = {"items": results}
        else:
            results_dict = {"data": str(results)}

        # Build export structure with metadata
        export_data = {
            "metadata": {
                "automation_name": automation_name,
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "1.0"
            },
            "results": results_dict
        }

        # Add configuration metadata if provided
        if config:
            export_data["metadata"]["configuration"] = {
                "task_name": config.task_name,
                "enabled": config.enabled,
                "created_at": config.created_at,
                "last_modified": config.last_modified
            }

        # Exclude sensitive data if requested
        if exclude_sensitive:
            export_data = self._exclude_sensitive_data(export_data)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{automation_name}_{timestamp}.json"
        filepath = self.export_dir / filename

        # Write to file
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        return str(filepath)

    def export_results_csv(
        self,
        results: List[Dict[str, Any]],
        automation_name: str,
        config: Optional[AutomationConfig] = None,
        exclude_sensitive: bool = True
    ) -> str:
        """
        Export results as CSV with metadata header.

        Args:
            results: List of dictionaries to export
            automation_name: Name of the automation task
            config: Optional automation configuration to include as metadata
            exclude_sensitive: Whether to exclude sensitive data

        Returns:
            Path to the exported file
        """
        if not isinstance(results, list):
            raise ValueError("Results must be a list of dictionaries for CSV export")

        if len(results) == 0:
            raise ValueError("Results list cannot be empty")

        # Exclude sensitive data if requested
        if exclude_sensitive:
            results = self._exclude_sensitive_data_from_list(results)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{automation_name}_{timestamp}.csv"
        filepath = self.export_dir / filename

        # Write to CSV file
        with open(filepath, "w", newline="") as f:
            # Write metadata as comments
            f.write(f"# Automation: {automation_name}\n")
            f.write(f"# Exported: {datetime.now().isoformat()}\n")
            if config:
                f.write(f"# Configuration: {config.task_name}\n")
            f.write("\n")

            # Get all unique keys from results
            fieldnames = set()
            for result in results:
                fieldnames.update(result.keys())
            fieldnames = sorted(list(fieldnames))

            # Write CSV data
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        return str(filepath)

    def export_execution_record(
        self,
        record: ExecutionRecord,
        exclude_sensitive: bool = True
    ) -> str:
        """
        Export an execution record with metadata.

        Args:
            record: ExecutionRecord to export
            exclude_sensitive: Whether to exclude sensitive data

        Returns:
            Path to the exported file
        """
        record_dict = asdict(record)

        # Build export structure
        export_data = {
            "metadata": {
                "record_type": "execution_record",
                "export_timestamp": datetime.now().isoformat(),
                "export_version": "1.0"
            },
            "record": record_dict
        }

        # Exclude sensitive data if requested
        if exclude_sensitive:
            export_data = self._exclude_sensitive_data(export_data)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"execution_{record.automation_name}_{timestamp}.json"
        filepath = self.export_dir / filename

        # Write to file
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        return str(filepath)

    def _exclude_sensitive_data(self, data: Any) -> Any:
        """
        Recursively exclude sensitive data from a data structure.

        Args:
            data: Data structure to filter

        Returns:
            Filtered data structure
        """
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if not self._is_sensitive_key(key):
                    filtered[key] = self._exclude_sensitive_data(value)
            return filtered
        elif isinstance(data, list):
            return [self._exclude_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Mask sensitive data in string values
            return ErrorHandler.mask_sensitive_data(data)
        else:
            return data

    def _exclude_sensitive_data_from_list(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Exclude sensitive data from a list of dictionaries.

        Args:
            items: List of dictionaries to filter

        Returns:
            Filtered list of dictionaries
        """
        filtered_items = []
        for item in items:
            filtered_item = {}
            for key, value in item.items():
                if not self._is_sensitive_key(key):
                    # Mask sensitive data in string values
                    if isinstance(value, str):
                        filtered_item[key] = ErrorHandler.mask_sensitive_data(value)
                    else:
                        filtered_item[key] = value
            filtered_items.append(filtered_item)
        return filtered_items

    def _is_sensitive_key(self, key: str) -> bool:
        """
        Check if a key contains sensitive information.

        Args:
            key: Key to check

        Returns:
            True if key is sensitive, False otherwise
        """
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in self.SENSITIVE_KEYWORDS)

    def export_with_metadata(
        self,
        results: Any,
        automation_name: str,
        automation_id: str,
        config: Optional[AutomationConfig] = None,
        execution_record: Optional[ExecutionRecord] = None,
        exclude_sensitive: bool = True,
        format: str = "json"
    ) -> str:
        """
        Export results with comprehensive metadata.

        Args:
            results: Results to export
            automation_name: Name of the automation
            automation_id: ID of the automation
            config: Optional automation configuration
            execution_record: Optional execution record
            exclude_sensitive: Whether to exclude sensitive data
            format: Export format ('json' or 'csv')

        Returns:
            Path to the exported file
        """
        # Build comprehensive metadata
        metadata = {
            "automation_name": automation_name,
            "automation_id": automation_id,
            "export_timestamp": datetime.now().isoformat(),
            "export_version": "1.0"
        }

        # Add configuration metadata
        if config:
            metadata["configuration"] = {
                "task_name": config.task_name,
                "enabled": config.enabled,
                "created_at": config.created_at,
                "last_modified": config.last_modified,
                "options": config.options if not exclude_sensitive else {}
            }

        # Add execution metadata
        if execution_record:
            metadata["execution"] = {
                "execution_id": execution_record.execution_id,
                "timestamp": execution_record.timestamp,
                "success": execution_record.success,
                "duration_seconds": execution_record.duration_seconds,
                "items_processed": execution_record.items_processed,
                "time_saved_minutes": execution_record.time_saved_minutes
            }

        # Convert results to appropriate format
        if hasattr(results, '__dataclass_fields__'):
            results_data = asdict(results)
        elif isinstance(results, dict):
            results_data = results
        elif isinstance(results, list):
            results_data = results
        else:
            results_data = str(results)

        # Exclude sensitive data if requested
        if exclude_sensitive:
            results_data = self._exclude_sensitive_data(results_data)

        # Export based on format
        if format.lower() == "csv" and isinstance(results_data, list):
            return self.export_results_csv(
                results_data,
                automation_name,
                config,
                exclude_sensitive=False  # Already excluded above
            )
        else:
            # Build final export structure
            export_data = {
                "metadata": metadata,
                "results": results_data
            }

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{automation_name}_{automation_id}_{timestamp}.json"
            filepath = self.export_dir / filename

            # Write to file
            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

            return str(filepath)

    def get_export_directory(self) -> str:
        """
        Get the export directory path.

        Returns:
            Path to the export directory
        """
        return str(self.export_dir)

    def list_exports(self) -> List[str]:
        """
        List all exported files.

        Returns:
            List of exported file paths
        """
        if not self.export_dir.exists():
            return []

        exports = []
        for file in self.export_dir.glob("*"):
            if file.is_file():
                exports.append(str(file))

        return sorted(exports, reverse=True)  # Most recent first

    def delete_export(self, filepath: str) -> bool:
        """
        Delete an exported file.

        Args:
            filepath: Path to the file to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path = Path(filepath)
            if path.exists() and path.parent == self.export_dir:
                path.unlink()
                return True
            return False
        except Exception:
            return False

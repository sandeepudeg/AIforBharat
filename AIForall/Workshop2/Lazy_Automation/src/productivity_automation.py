"""Productivity automation module for data processing and clipboard management."""

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import deque


class ReportGenerator:
    """Generates reports from CSV/Excel files with charts and statistics."""

    @staticmethod
    def parse_csv(file_path: str) -> Tuple[List[str], List[List[str]]]:
        """
        Parse a CSV file and return headers and rows.

        Args:
            file_path: Path to the CSV file

        Returns:
            Tuple of (headers, rows) where headers is a list of column names
            and rows is a list of lists containing row data

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file is not a valid CSV
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows:
                raise ValueError("CSV file is empty")

            headers = rows[0]
            data_rows = rows[1:]

            return headers, data_rows
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")

    @staticmethod
    def generate_statistics(headers: List[str], rows: List[List[str]]) -> Dict[str, Any]:
        """
        Generate statistics from parsed CSV data.

        Args:
            headers: List of column names
            rows: List of data rows

        Returns:
            Dictionary containing statistics (row count, column count, etc.)
        """
        stats = {
            "row_count": len(rows),
            "column_count": len(headers),
            "columns": headers,
            "numeric_columns": [],
            "text_columns": [],
        }

        # Identify numeric and text columns
        for col_idx, header in enumerate(headers):
            is_numeric = True
            for row in rows:
                if col_idx < len(row) and row[col_idx].strip():
                    try:
                        float(row[col_idx])
                    except ValueError:
                        is_numeric = False
                        break

            if is_numeric:
                stats["numeric_columns"].append(header)
            else:
                stats["text_columns"].append(header)

        return stats

    @staticmethod
    def export_to_json(headers: List[str], rows: List[List[str]]) -> str:
        """
        Export CSV data to JSON format.

        Args:
            headers: List of column names
            rows: List of data rows

        Returns:
            JSON string representation of the data
        """
        data = []
        for row in rows:
            row_dict = {}
            for idx, header in enumerate(headers):
                row_dict[header] = row[idx] if idx < len(row) else ""
            data.append(row_dict)

        return json.dumps(data, indent=2)


class LogCleaner:
    """Parses and analyzes log files to highlight errors and warnings."""

    # Log level patterns
    ERROR_PATTERNS = [
        r'\bERROR\b',
        r'\bFATAL\b',
        r'\bCRITICAL\b',
        r'\bException\b',
        r'\bFailed\b',
    ]

    WARNING_PATTERNS = [
        r'\bWARNING\b',
        r'\bWARN\b',
        r'\bDeprecated\b',
    ]

    @staticmethod
    def parse_log_file(file_path: str) -> List[str]:
        """
        Parse a log file and return all lines.

        Args:
            file_path: Path to the log file

        Returns:
            List of log lines

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            return lines
        except IOError as e:
            raise IOError(f"Cannot read log file: {e}")

    @staticmethod
    def extract_errors(lines: List[str]) -> List[Dict[str, Any]]:
        """
        Extract error entries from log lines.

        Args:
            lines: List of log lines

        Returns:
            List of dictionaries containing error information
        """
        errors = []

        for line_num, line in enumerate(lines, 1):
            for pattern in LogCleaner.ERROR_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append({
                        "line_number": line_num,
                        "content": line.strip(),
                        "level": "ERROR"
                    })
                    break

        return errors

    @staticmethod
    def extract_warnings(lines: List[str]) -> List[Dict[str, Any]]:
        """
        Extract warning entries from log lines.

        Args:
            lines: List of log lines

        Returns:
            List of dictionaries containing warning information
        """
        warnings = []

        for line_num, line in enumerate(lines, 1):
            for pattern in LogCleaner.WARNING_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    warnings.append({
                        "line_number": line_num,
                        "content": line.strip(),
                        "level": "WARNING"
                    })
                    break

        return warnings

    @staticmethod
    def analyze_log(file_path: str) -> Dict[str, Any]:
        """
        Analyze a log file and return summary.

        Args:
            file_path: Path to the log file

        Returns:
            Dictionary containing analysis results
        """
        lines = LogCleaner.parse_log_file(file_path)
        errors = LogCleaner.extract_errors(lines)
        warnings = LogCleaner.extract_warnings(lines)

        return {
            "total_lines": len(lines),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }


class ClipboardEnhancer:
    """Manages multi-item clipboard history with search and recall."""

    def __init__(self, max_items: int = 100):
        """
        Initialize the clipboard enhancer.

        Args:
            max_items: Maximum number of items to store in history
        """
        self.max_items = max_items
        self.history: deque = deque(maxlen=max_items)

    def add_item(self, content: str, source_task: str = "", tags: List[str] = None) -> None:
        """
        Add an item to clipboard history.

        Args:
            content: The clipboard content
            source_task: Optional source task identifier
            tags: Optional list of tags for the item
        """
        if not isinstance(content, str):
            raise ValueError("Content must be a string")

        if tags is None:
            tags = []

        item = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "source_task": source_task,
            "tags": tags,
        }

        self.history.appendleft(item)

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the clipboard history in reverse chronological order.

        Returns:
            List of clipboard items (most recent first)
        """
        return list(self.history)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search clipboard history for items matching the query.

        Args:
            query: Search query string

        Returns:
            List of matching clipboard items
        """
        if not isinstance(query, str):
            raise ValueError("Query must be a string")

        if not query.strip():
            return []

        query_lower = query.lower()
        results = []

        for item in self.history:
            if (query_lower in item["content"].lower() or
                query_lower in item["source_task"].lower() or
                any(query_lower in tag.lower() for tag in item["tags"])):
                results.append(item)

        return results

    def get_item_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a clipboard item by index.

        Args:
            index: Index in the history (0 is most recent)

        Returns:
            The clipboard item or None if index is out of range
        """
        if not isinstance(index, int) or index < 0:
            return None

        history_list = list(self.history)
        if index >= len(history_list):
            return None

        return history_list[index]

    def clear_history(self) -> None:
        """Clear all clipboard history."""
        self.history.clear()

    def get_history_size(self) -> int:
        """Get the current number of items in history."""
        return len(self.history)

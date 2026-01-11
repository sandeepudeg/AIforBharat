"""Constraint persistence layer for saving and loading configurations."""

import json
import os
from typing import List, Optional
from src.models import Constraint


class PersistenceManager:
    """Manages saving and loading constraint configurations."""

    DATA_DIR = "data"

    @staticmethod
    def _ensure_data_dir() -> None:
        """Ensure data directory exists."""
        if not os.path.exists(PersistenceManager.DATA_DIR):
            os.makedirs(PersistenceManager.DATA_DIR)

    @staticmethod
    def _get_config_path(name: str) -> str:
        """Get the file path for a configuration."""
        # Sanitize name to prevent directory traversal
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_", " "))
        if not safe_name:
            safe_name = "config"
        return os.path.join(PersistenceManager.DATA_DIR, f"{safe_name}.json")

    @staticmethod
    def save_configuration(name: str, constraint: Constraint) -> bool:
        """Save a constraint configuration to JSON.

        Args:
            name: Configuration name
            constraint: Constraint object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            PersistenceManager._ensure_data_dir()

            # Validate name
            if not name or not isinstance(name, str):
                return False

            # Convert Constraint to dict
            config_data = {
                "name": name,
                "data_structure": constraint.data_structure,
                "read_write_ratio": constraint.read_write_ratio,
                "consistency_level": constraint.consistency_level,
                "query_complexity": constraint.query_complexity,
                "scale_gb": constraint.scale_gb,
                "latency_ms": constraint.latency_ms,
                "team_expertise": constraint.team_expertise,
                "requires_persistence": constraint.requires_persistence,
            }

            # Save to JSON file
            config_path = PersistenceManager._get_config_path(name)
            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=2)

            return True
        except (IOError, OSError, TypeError, ValueError):
            return False

    @staticmethod
    def load_configuration(name: str) -> Optional[Constraint]:
        """Load a constraint configuration from JSON.

        Args:
            name: Configuration name to load

        Returns:
            Constraint object if successful, None otherwise
        """
        try:
            config_path = PersistenceManager._get_config_path(name)

            # Check if file exists
            if not os.path.exists(config_path):
                return None

            # Load JSON
            with open(config_path, "r") as f:
                config_data = json.load(f)

            # Convert to Constraint object
            constraint = Constraint(
                data_structure=config_data["data_structure"],
                read_write_ratio=config_data["read_write_ratio"],
                consistency_level=config_data["consistency_level"],
                query_complexity=config_data["query_complexity"],
                scale_gb=config_data["scale_gb"],
                latency_ms=config_data["latency_ms"],
                team_expertise=config_data["team_expertise"],
                requires_persistence=config_data.get("requires_persistence", True),
            )

            return constraint
        except (IOError, OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
            return None

    @staticmethod
    def list_configurations() -> List[str]:
        """List all saved configurations.

        Returns:
            List of configuration names
        """
        try:
            PersistenceManager._ensure_data_dir()

            if not os.path.exists(PersistenceManager.DATA_DIR):
                return []

            # List files in data directory
            files = os.listdir(PersistenceManager.DATA_DIR)
            configs = []

            for file in files:
                if file.endswith(".json"):
                    # Extract name from filename
                    name = file[:-5]  # Remove .json extension
                    configs.append(name)

            return sorted(configs)
        except (IOError, OSError):
            return []

    @staticmethod
    def delete_configuration(name: str) -> bool:
        """Delete a saved configuration.

        Args:
            name: Configuration name to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = PersistenceManager._get_config_path(name)

            # Check if file exists
            if not os.path.exists(config_path):
                return False

            # Delete file
            os.remove(config_path)
            return True
        except (IOError, OSError):
            return False

"""Web and Cloud automation module for downloads, form filling, and cloud storage management."""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from urllib.parse import urlparse
from src.data_models import FileOperationResult


class BulkDownloader:
    """Handles batch downloading of resources from URLs."""

    @staticmethod
    def validate_urls(urls: List[str]) -> Tuple[bool, str]:
        """
        Validate a list of URLs.

        Args:
            urls: List of URLs to validate

        Returns:
            Tuple of (is_valid, error_message)

        Raises:
            ValueError: If urls is not a list
        """
        if not isinstance(urls, list):
            raise ValueError("urls must be a list")

        if len(urls) == 0:
            return False, "URL list cannot be empty"

        for url in urls:
            if not isinstance(url, str) or not url.strip():
                return False, "All URLs must be non-empty strings"

            # Basic URL validation
            if not (url.startswith("http://") or url.startswith("https://")):
                return False, f"Invalid URL format: {url}"

        return True, ""

    @staticmethod
    def extract_filename_from_url(url: str) -> str:
        """
        Extract filename from URL.

        Args:
            url: The URL to extract filename from

        Returns:
            Filename extracted from URL or a default name

        Raises:
            ValueError: If URL is invalid
        """
        if not isinstance(url, str) or not url.strip():
            raise ValueError("url must be a non-empty string")

        try:
            parsed = urlparse(url)
            path = parsed.path
            filename = os.path.basename(path)

            # If no filename in path, use a default
            if not filename or filename == "":
                filename = f"download_{hash(url) % 10000}.bin"

            return filename
        except Exception as e:
            raise ValueError(f"Cannot extract filename from URL: {e}")

    @staticmethod
    def organize_downloads(directory: str, urls: List[str]) -> FileOperationResult:
        """
        Organize downloaded files into folders by type.

        Args:
            directory: Directory where downloads are stored
            urls: List of URLs that were downloaded

        Returns:
            FileOperationResult with details of organized files

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
            ValueError: If urls list is invalid
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        is_valid, error_msg = BulkDownloader.validate_urls(urls)
        if not is_valid:
            raise ValueError(error_msg)

        processed_count = 0
        error_count = 0
        details = []

        # Create type-based subdirectories
        type_dirs = {
            "pdf": os.path.join(directory, "PDFs"),
            "image": os.path.join(directory, "Images"),
            "video": os.path.join(directory, "Videos"),
            "document": os.path.join(directory, "Documents"),
            "archive": os.path.join(directory, "Archives"),
            "other": os.path.join(directory, "Other"),
        }

        for type_dir in type_dirs.values():
            os.makedirs(type_dir, exist_ok=True)

        # Organize existing files
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    # Determine file type based on extension
                    ext = os.path.splitext(filename)[1].lower()
                    
                    if ext == ".pdf":
                        dest_dir = type_dirs["pdf"]
                    elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"]:
                        dest_dir = type_dirs["image"]
                    elif ext in [".mp4", ".avi", ".mkv", ".mov", ".flv"]:
                        dest_dir = type_dirs["video"]
                    elif ext in [".doc", ".docx", ".txt", ".xlsx", ".xls", ".ppt", ".pptx"]:
                        dest_dir = type_dirs["document"]
                    elif ext in [".zip", ".rar", ".7z", ".tar", ".gz"]:
                        dest_dir = type_dirs["archive"]
                    else:
                        dest_dir = type_dirs["other"]

                    destination = os.path.join(dest_dir, filename)
                    
                    # Only move if not already in the correct directory
                    if os.path.dirname(file_path) != dest_dir:
                        shutil.move(file_path, destination)
                        processed_count += 1
                        details.append({
                            "file": filename,
                            "destination": destination,
                            "status": "success"
                        })
                except Exception as e:
                    error_count += 1
                    details.append({
                        "file": filename,
                        "status": "error",
                        "error": str(e)
                    })

        return FileOperationResult(
            success=error_count == 0,
            processed_count=processed_count,
            error_count=error_count,
            details=details
        )


class AutoFormFiller:
    """Handles profile storage and automatic form field population."""

    def __init__(self):
        """Initialize the AutoFormFiller with empty profiles."""
        self.profiles: Dict[str, Dict[str, str]] = {}

    def create_profile(self, profile_id: str, profile_data: Dict[str, str]) -> None:
        """
        Create a user profile for form filling.

        Args:
            profile_id: Unique identifier for the profile
            profile_data: Dictionary of field names to values

        Returns:
            None

        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("profile_id must be a non-empty string")

        if not isinstance(profile_data, dict):
            raise ValueError("profile_data must be a dictionary")

        if len(profile_data) == 0:
            raise ValueError("profile_data cannot be empty")

        # Validate all values are strings
        for key, value in profile_data.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("All profile keys and values must be strings")

        self.profiles[profile_id] = profile_data.copy()

    def get_profile(self, profile_id: str) -> Optional[Dict[str, str]]:
        """
        Get a profile by ID.

        Args:
            profile_id: ID of the profile to retrieve

        Returns:
            Profile dictionary if found, None otherwise
        """
        return self.profiles.get(profile_id)

    def populate_form(self, profile_id: str, form_fields: Dict[str, str]) -> Dict[str, str]:
        """
        Populate form fields using a stored profile.

        Args:
            profile_id: ID of the profile to use
            form_fields: Dictionary of form field names to populate

        Returns:
            Dictionary with populated form fields

        Raises:
            ValueError: If profile_id or form_fields are invalid
            KeyError: If profile_id does not exist
        """
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("profile_id must be a non-empty string")

        if not isinstance(form_fields, dict):
            raise ValueError("form_fields must be a dictionary")

        if profile_id not in self.profiles:
            raise KeyError(f"Profile not found: {profile_id}")

        profile = self.profiles[profile_id]
        populated_form = {}

        # Match form fields with profile data
        for field_name in form_fields.keys():
            # Try exact match first
            if field_name in profile:
                populated_form[field_name] = profile[field_name]
            else:
                # Try case-insensitive match
                field_lower = field_name.lower()
                for profile_key, profile_value in profile.items():
                    if profile_key.lower() == field_lower:
                        populated_form[field_name] = profile_value
                        break

        return populated_form

    def update_profile(self, profile_id: str, updates: Dict[str, str]) -> None:
        """
        Update an existing profile.

        Args:
            profile_id: ID of the profile to update
            updates: Dictionary of fields to update

        Returns:
            None

        Raises:
            ValueError: If parameters are invalid
            KeyError: If profile_id does not exist
        """
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("profile_id must be a non-empty string")

        if not isinstance(updates, dict):
            raise ValueError("updates must be a dictionary")

        if profile_id not in self.profiles:
            raise KeyError(f"Profile not found: {profile_id}")

        # Validate all update values are strings
        for key, value in updates.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("All update keys and values must be strings")

        self.profiles[profile_id].update(updates)

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a profile by ID.

        Args:
            profile_id: ID of the profile to delete

        Returns:
            True if profile was deleted, False if not found
        """
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            return True
        return False

    def get_all_profiles(self) -> Dict[str, Dict[str, str]]:
        """
        Get all stored profiles.

        Returns:
            Dictionary of all profiles
        """
        return {pid: pdata.copy() for pid, pdata in self.profiles.items()}

    def clear_profiles(self) -> None:
        """Clear all profiles."""
        self.profiles.clear()


class CloudSyncCleanup:
    """Handles cloud storage archival and cleanup."""

    def __init__(self):
        """Initialize the CloudSyncCleanup."""
        self.archive_log: List[Dict[str, Any]] = []

    def archive_old_files(self, directory: str, days_old: int) -> FileOperationResult:
        """
        Archive files older than specified number of days.

        Args:
            directory: Directory to scan for old files
            days_old: Number of days to consider as "old"

        Returns:
            FileOperationResult with details of archived files

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
            ValueError: If days_old is invalid
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        if not isinstance(days_old, int) or days_old < 0:
            raise ValueError("days_old must be a non-negative integer")

        processed_count = 0
        error_count = 0
        details = []

        # Create archive directory
        archive_dir = os.path.join(directory, "archive")
        os.makedirs(archive_dir, exist_ok=True)

        # Get current time
        current_time = datetime.now().timestamp()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Skip the archive directory itself
            if file_path == archive_dir:
                continue

            if os.path.isfile(file_path):
                try:
                    # Get file modification time
                    file_mtime = os.path.getmtime(file_path)

                    # Check if file is older than cutoff
                    if file_mtime < cutoff_time:
                        destination = os.path.join(archive_dir, filename)
                        shutil.move(file_path, destination)
                        processed_count += 1

                        # Log the archive action
                        self.archive_log.append({
                            "filename": filename,
                            "archived_at": datetime.now().isoformat(),
                            "original_path": file_path,
                            "archive_path": destination,
                            "file_age_days": (current_time - file_mtime) / (24 * 60 * 60),
                            "status": "success"
                        })

                        details.append({
                            "file": filename,
                            "destination": destination,
                            "status": "success"
                        })
                except Exception as e:
                    error_count += 1
                    details.append({
                        "file": filename,
                        "status": "error",
                        "error": str(e)
                    })

        return FileOperationResult(
            success=error_count == 0,
            processed_count=processed_count,
            error_count=error_count,
            details=details
        )

    def get_archive_log(self) -> List[Dict[str, Any]]:
        """
        Get the archive log.

        Returns:
            List of archive log entries
        """
        return self.archive_log.copy()

    def clear_archive_log(self) -> None:
        """Clear the archive log."""
        self.archive_log.clear()

    def get_archive_summary(self) -> Dict[str, Any]:
        """
        Get a summary of archived files.

        Returns:
            Dictionary with archive statistics
        """
        total_archived = len(self.archive_log)
        successful = sum(1 for entry in self.archive_log if entry.get("status") == "success")
        failed = total_archived - successful

        return {
            "total_archived": total_archived,
            "successful": successful,
            "failed": failed,
            "archive_entries": self.archive_log
        }

    def restore_from_archive(self, archive_dir: str, filename: str, restore_dir: str) -> bool:
        """
        Restore a file from archive.

        Args:
            archive_dir: Path to the archive directory
            filename: Name of the file to restore
            restore_dir: Directory to restore the file to

        Returns:
            True if file was restored, False otherwise

        Raises:
            FileNotFoundError: If archive directory or file does not exist
            NotADirectoryError: If paths are not directories
        """
        if not os.path.exists(archive_dir):
            raise FileNotFoundError(f"Archive directory not found: {archive_dir}")

        if not os.path.isdir(archive_dir):
            raise NotADirectoryError(f"Path is not a directory: {archive_dir}")

        if not os.path.exists(restore_dir):
            raise FileNotFoundError(f"Restore directory not found: {restore_dir}")

        if not os.path.isdir(restore_dir):
            raise NotADirectoryError(f"Path is not a directory: {restore_dir}")

        archived_file = os.path.join(archive_dir, filename)

        if not os.path.exists(archived_file):
            return False

        try:
            destination = os.path.join(restore_dir, filename)
            shutil.move(archived_file, destination)
            return True
        except Exception:
            return False

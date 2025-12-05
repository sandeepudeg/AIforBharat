"""File automation module for bulk operations on files."""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from src.file_service import FileService
from src.data_models import FileOperationResult


class BulkRenamer:
    """Handles bulk file renaming with preview and execution."""

    @staticmethod
    def generate_preview(directory: str, pattern: str, replacement: str) -> List[Tuple[str, str]]:
        """
        Generate a preview of rename operations without applying them.

        Args:
            directory: Directory containing files to rename
            pattern: Regex pattern to match in filenames
            replacement: Replacement string for matched pattern

        Returns:
            List of tuples (original_filename, new_filename)

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        preview = []
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    new_filename = re.sub(pattern, replacement, filename)
                    if new_filename != filename:
                        preview.append((filename, new_filename))
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        return preview

    @staticmethod
    def apply_rename(directory: str, pattern: str, replacement: str) -> FileOperationResult:
        """
        Apply bulk rename operations to files in a directory.

        Args:
            directory: Directory containing files to rename
            pattern: Regex pattern to match in filenames
            replacement: Replacement string for matched pattern

        Returns:
            FileOperationResult with details of renamed files

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
            ValueError: If regex pattern is invalid
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Validate regex pattern before processing
        try:
            re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        processed_count = 0
        error_count = 0
        details = []

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    new_filename = re.sub(pattern, replacement, filename)
                    if new_filename != filename:
                        new_file_path = os.path.join(directory, new_filename)
                        os.rename(file_path, new_file_path)
                        processed_count += 1
                        details.append({
                            "original": filename,
                            "renamed": new_filename,
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


class AutoOrganizer:
    """Handles automatic file organization by type."""

    @staticmethod
    def organize_files(directory: str, create_subdirs: bool = True) -> FileOperationResult:
        """
        Organize files in a directory by type into categorized subdirectories.

        Args:
            directory: Directory containing files to organize
            create_subdirs: Whether to create subdirectories for each type

        Returns:
            FileOperationResult with details of organized files

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        processed_count = 0
        error_count = 0
        details = []

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    file_type = FileService.detect_file_type(file_path)
                    
                    if create_subdirs:
                        type_dir = os.path.join(directory, file_type)
                        os.makedirs(type_dir, exist_ok=True)
                        destination = os.path.join(type_dir, filename)
                    else:
                        destination = file_path

                    if destination != file_path:
                        FileService.move_file(file_path, destination)
                        processed_count += 1
                        details.append({
                            "file": filename,
                            "type": file_type,
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

    @staticmethod
    def get_file_type_distribution(directory: str) -> Dict[str, int]:
        """
        Get distribution of file types in a directory.

        Args:
            directory: Directory to analyze

        Returns:
            Dictionary mapping file type to count

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        distribution = {}

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                try:
                    file_type = FileService.detect_file_type(file_path)
                    distribution[file_type] = distribution.get(file_type, 0) + 1
                except Exception:
                    # Skip files that cannot be analyzed
                    continue

        return distribution


class DuplicateCleaner:
    """Handles detection and removal of duplicate files."""

    @staticmethod
    def find_duplicates(directory: str) -> List[List[str]]:
        """
        Find duplicate files in a directory.

        Args:
            directory: Directory to search for duplicates

        Returns:
            List of lists, where each inner list contains paths of duplicate files

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        return FileService.find_duplicates(directory)

    @staticmethod
    def remove_duplicates(directory: str, keep_first: bool = True) -> FileOperationResult:
        """
        Remove duplicate files, keeping only one copy of each.

        Args:
            directory: Directory to clean
            keep_first: If True, keep the first file; if False, keep the last

        Returns:
            FileOperationResult with details of removed duplicates

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        duplicates = DuplicateCleaner.find_duplicates(directory)
        processed_count = 0
        error_count = 0
        details = []

        for duplicate_group in duplicates:
            # Sort for consistent behavior
            sorted_files = sorted(duplicate_group)
            
            # Determine which file to keep
            if keep_first:
                keep_file = sorted_files[0]
                remove_files = sorted_files[1:]
            else:
                keep_file = sorted_files[-1]
                remove_files = sorted_files[:-1]

            # Remove duplicates
            for file_to_remove in remove_files:
                try:
                    os.remove(file_to_remove)
                    processed_count += 1
                    details.append({
                        "removed": file_to_remove,
                        "kept": keep_file,
                        "status": "success"
                    })
                except Exception as e:
                    error_count += 1
                    details.append({
                        "file": file_to_remove,
                        "status": "error",
                        "error": str(e)
                    })

        return FileOperationResult(
            success=error_count == 0,
            processed_count=processed_count,
            error_count=error_count,
            details=details
        )

    @staticmethod
    def get_duplicate_summary(directory: str) -> Dict[str, any]:
        """
        Get a summary of duplicates in a directory.

        Args:
            directory: Directory to analyze

        Returns:
            Dictionary with duplicate statistics

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        duplicates = DuplicateCleaner.find_duplicates(directory)
        
        total_duplicate_files = sum(len(group) - 1 for group in duplicates)
        total_duplicate_groups = len(duplicates)
        
        # Calculate space that could be saved
        space_saved = 0
        for duplicate_group in duplicates:
            for file_path in duplicate_group[1:]:  # Skip the first (kept) file
                try:
                    space_saved += os.path.getsize(file_path)
                except Exception:
                    continue

        return {
            "duplicate_groups": total_duplicate_groups,
            "duplicate_files": total_duplicate_files,
            "space_saved_bytes": space_saved,
            "space_saved_mb": round(space_saved / (1024 * 1024), 2)
        }

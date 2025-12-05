"""File service layer for file operations and utilities."""

import hashlib
import mimetypes
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class FileService:
    """Service for file operations including hashing, type detection, and duplicate finding."""

    # File type categories based on extensions
    FILE_TYPE_CATEGORIES = {
        'pdf': ['pdf'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico', 'tiff'],
        'video': ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'mpg', 'mpeg'],
        'document': ['doc', 'docx', 'txt', 'rtf', 'odt', 'pages', 'tex'],
        'archive': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso'],
        'spreadsheet': ['xls', 'xlsx', 'csv', 'ods', 'numbers'],
        'presentation': ['ppt', 'pptx', 'odp', 'key'],
        'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma'],
        'code': ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs', 'rb', 'php', 'html', 'css', 'json', 'xml', 'yaml', 'yml'],
    }

    @staticmethod
    def compute_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """
        Compute hash of a file using specified algorithm.

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use (default: sha256)

        Returns:
            Hexadecimal hash string

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
        except IOError as e:
            raise IOError(f"Cannot read file {file_path}: {e}")

        return hash_obj.hexdigest()

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """
        Detect file type based on extension and MIME type.

        Args:
            file_path: Path to the file

        Returns:
            File type category (e.g., 'pdf', 'image', 'video', 'document', 'archive')
            Returns 'unknown' if type cannot be determined

        Raises:
            FileNotFoundError: If file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file extension
        file_ext = Path(file_path).suffix.lstrip('.').lower()

        # Check against known categories
        for category, extensions in FileService.FILE_TYPE_CATEGORIES.items():
            if file_ext in extensions:
                return category

        # Try MIME type detection as fallback
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith('image/'):
                return 'image'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('text/'):
                return 'document'
            elif mime_type.startswith('application/'):
                if 'pdf' in mime_type:
                    return 'pdf'
                elif 'zip' in mime_type or 'archive' in mime_type:
                    return 'archive'

        return 'unknown'

    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """
        Move a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if move was successful

        Raises:
            FileNotFoundError: If source file does not exist
            IOError: If move operation fails
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source file not found: {source}")

        try:
            # Create destination directory if it doesn't exist
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            shutil.move(source, destination)
            return True
        except Exception as e:
            raise IOError(f"Failed to move file from {source} to {destination}: {e}")

    @staticmethod
    def find_duplicates(directory: str) -> List[List[str]]:
        """
        Find duplicate files in a directory based on file hash.

        Args:
            directory: Directory to search for duplicates

        Returns:
            List of lists, where each inner list contains paths of duplicate files
            Empty list if no duplicates found

        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Dictionary to store hash -> list of file paths
        hash_map: Dict[str, List[str]] = defaultdict(list)

        # Walk through directory and compute hashes
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_hash = FileService.compute_file_hash(file_path)
                    hash_map[file_hash].append(file_path)
                except (IOError, FileNotFoundError):
                    # Skip files that cannot be read
                    continue

        # Return only groups with duplicates (more than 1 file)
        duplicates = [files for files in hash_map.values() if len(files) > 1]
        return duplicates

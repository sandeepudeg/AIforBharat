"""Tests for File Automation Module."""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st
from src.file_automation import BulkRenamer, AutoOrganizer, DuplicateCleaner
from src.data_models import FileOperationResult


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_files_for_rename(temp_dir):
    """Create sample files for rename testing."""
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"file_{i}_old.txt")
        with open(file_path, "w") as f:
            f.write(f"content {i}")
        files.append(file_path)
    return files


@pytest.fixture
def sample_files_for_organize(temp_dir):
    """Create sample files of different types for organize testing."""
    files = {}
    
    # Create PDF file
    pdf_file = os.path.join(temp_dir, "document.pdf")
    with open(pdf_file, "wb") as f:
        f.write(b"%PDF-1.4\nfake pdf")
    files["pdf"] = pdf_file
    
    # Create image file
    image_file = os.path.join(temp_dir, "photo.png")
    with open(image_file, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
    files["image"] = image_file
    
    # Create text file
    text_file = os.path.join(temp_dir, "notes.txt")
    with open(text_file, "w") as f:
        f.write("text content")
    files["text"] = text_file
    
    # Create video file
    video_file = os.path.join(temp_dir, "movie.mp4")
    with open(video_file, "wb") as f:
        f.write(b"fake video")
    files["video"] = video_file
    
    return files


@pytest.fixture
def sample_files_for_duplicates(temp_dir):
    """Create sample files with duplicates for testing."""
    files = {}
    
    # Create unique files
    unique1 = os.path.join(temp_dir, "unique1.txt")
    with open(unique1, "w") as f:
        f.write("unique content 1")
    files["unique1"] = unique1
    
    unique2 = os.path.join(temp_dir, "unique2.txt")
    with open(unique2, "w") as f:
        f.write("unique content 2")
    files["unique2"] = unique2
    
    # Create duplicate files
    dup_content = "duplicate content"
    dup1 = os.path.join(temp_dir, "dup1.txt")
    with open(dup1, "w") as f:
        f.write(dup_content)
    files["dup1"] = dup1
    
    dup2 = os.path.join(temp_dir, "dup2.txt")
    with open(dup2, "w") as f:
        f.write(dup_content)
    files["dup2"] = dup2
    
    return files


# BulkRenamer Tests

def test_bulk_renamer_preview_basic(sample_files_for_rename):
    """Test generating preview for bulk rename."""
    temp_dir = os.path.dirname(sample_files_for_rename[0])
    preview = BulkRenamer.generate_preview(temp_dir, r"_old", "_new")
    
    assert len(preview) == 3
    for original, new in preview:
        assert "_old" in original
        assert "_new" in new


def test_bulk_renamer_preview_no_matches(sample_files_for_rename):
    """Test preview when pattern doesn't match any files."""
    temp_dir = os.path.dirname(sample_files_for_rename[0])
    preview = BulkRenamer.generate_preview(temp_dir, r"nomatch", "replacement")
    
    assert len(preview) == 0


def test_bulk_renamer_apply_rename(sample_files_for_rename):
    """Test applying bulk rename."""
    temp_dir = os.path.dirname(sample_files_for_rename[0])
    result = BulkRenamer.apply_rename(temp_dir, r"_old", "_new")
    
    assert isinstance(result, FileOperationResult)
    assert result.success is True
    assert result.processed_count == 3
    assert result.error_count == 0
    
    # Verify files were renamed
    for filename in os.listdir(temp_dir):
        assert "_new" in filename


def test_bulk_renamer_apply_rename_invalid_pattern(sample_files_for_rename):
    """Test that invalid regex pattern raises error."""
    temp_dir = os.path.dirname(sample_files_for_rename[0])
    
    with pytest.raises(ValueError):
        BulkRenamer.apply_rename(temp_dir, r"[invalid(regex", "replacement")


def test_bulk_renamer_nonexistent_directory():
    """Test that nonexistent directory raises error."""
    with pytest.raises(FileNotFoundError):
        BulkRenamer.generate_preview("/nonexistent/dir", "pattern", "replacement")


def test_bulk_renamer_not_a_directory(temp_dir):
    """Test that file path raises error."""
    file_path = os.path.join(temp_dir, "file.txt")
    with open(file_path, "w") as f:
        f.write("content")
    
    with pytest.raises(NotADirectoryError):
        BulkRenamer.generate_preview(file_path, "pattern", "replacement")


# AutoOrganizer Tests

def test_auto_organizer_organize_files(sample_files_for_organize):
    """Test organizing files by type."""
    temp_dir = os.path.dirname(list(sample_files_for_organize.values())[0])
    result = AutoOrganizer.organize_files(temp_dir)
    
    assert isinstance(result, FileOperationResult)
    assert result.success is True
    assert result.processed_count == 4
    assert result.error_count == 0
    
    # Verify subdirectories were created
    assert os.path.exists(os.path.join(temp_dir, "pdf"))
    assert os.path.exists(os.path.join(temp_dir, "image"))
    assert os.path.exists(os.path.join(temp_dir, "document"))
    assert os.path.exists(os.path.join(temp_dir, "video"))


def test_auto_organizer_get_file_type_distribution(sample_files_for_organize):
    """Test getting file type distribution."""
    temp_dir = os.path.dirname(list(sample_files_for_organize.values())[0])
    distribution = AutoOrganizer.get_file_type_distribution(temp_dir)
    
    assert distribution["pdf"] == 1
    assert distribution["image"] == 1
    assert distribution["document"] == 1
    assert distribution["video"] == 1


def test_auto_organizer_nonexistent_directory():
    """Test that nonexistent directory raises error."""
    with pytest.raises(FileNotFoundError):
        AutoOrganizer.organize_files("/nonexistent/dir")


def test_auto_organizer_not_a_directory(temp_dir):
    """Test that file path raises error."""
    file_path = os.path.join(temp_dir, "file.txt")
    with open(file_path, "w") as f:
        f.write("content")
    
    with pytest.raises(NotADirectoryError):
        AutoOrganizer.organize_files(file_path)


# DuplicateCleaner Tests

def test_duplicate_cleaner_find_duplicates(sample_files_for_duplicates):
    """Test finding duplicate files."""
    temp_dir = os.path.dirname(list(sample_files_for_duplicates.values())[0])
    duplicates = DuplicateCleaner.find_duplicates(temp_dir)
    
    assert len(duplicates) == 1
    assert len(duplicates[0]) == 2


def test_duplicate_cleaner_remove_duplicates(sample_files_for_duplicates):
    """Test removing duplicate files."""
    temp_dir = os.path.dirname(list(sample_files_for_duplicates.values())[0])
    result = DuplicateCleaner.remove_duplicates(temp_dir, keep_first=True)
    
    assert isinstance(result, FileOperationResult)
    assert result.success is True
    assert result.processed_count == 1
    assert result.error_count == 0
    
    # Verify only one duplicate was removed
    remaining_files = os.listdir(temp_dir)
    assert len(remaining_files) == 3  # 2 unique + 1 kept duplicate


def test_duplicate_cleaner_remove_duplicates_keep_last(sample_files_for_duplicates):
    """Test removing duplicates keeping the last file."""
    temp_dir = os.path.dirname(list(sample_files_for_duplicates.values())[0])
    result = DuplicateCleaner.remove_duplicates(temp_dir, keep_first=False)
    
    assert result.success is True
    assert result.processed_count == 1


def test_duplicate_cleaner_get_duplicate_summary(sample_files_for_duplicates):
    """Test getting duplicate summary."""
    temp_dir = os.path.dirname(list(sample_files_for_duplicates.values())[0])
    summary = DuplicateCleaner.get_duplicate_summary(temp_dir)
    
    assert summary["duplicate_groups"] == 1
    assert summary["duplicate_files"] == 1
    assert summary["space_saved_bytes"] > 0
    assert summary["space_saved_mb"] >= 0


def test_duplicate_cleaner_no_duplicates(temp_dir):
    """Test when there are no duplicates."""
    # Create unique files
    for i in range(3):
        with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
            f.write(f"unique content {i}")
    
    duplicates = DuplicateCleaner.find_duplicates(temp_dir)
    assert len(duplicates) == 0


def test_duplicate_cleaner_nonexistent_directory():
    """Test that nonexistent directory raises error."""
    with pytest.raises(FileNotFoundError):
        DuplicateCleaner.find_duplicates("/nonexistent/dir")


# Property-Based Tests

@given(
    pattern=st.text(min_size=1, max_size=20),
    replacement=st.text(min_size=0, max_size=20)
)
def test_rename_preview_accuracy(pattern, replacement):
    """
    **Feature: lazy-automation-platform, Property 1: Rename Preview Accuracy**
    
    For any set of filenames and rename pattern, the preview should display both 
    original and new filenames correctly.
    
    **Validates: Requirements 1.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with known names
        test_files = ["file1.txt", "file2.txt", "file3.txt"]
        for filename in test_files:
            with open(os.path.join(tmpdir, filename), "w") as f:
                f.write(f"content for {filename}")
        
        try:
            preview = BulkRenamer.generate_preview(tmpdir, pattern, replacement)
            
            # Verify preview structure and correctness
            for original, new in preview:
                # Both should be strings
                assert isinstance(original, str), f"Original should be string, got {type(original)}"
                assert isinstance(new, str), f"New should be string, got {type(new)}"
                
                # Original should exist in the directory
                assert original in test_files, f"Original filename {original} not in test files"
                
                # New filename should be different from original
                assert original != new, f"Original and new filenames should differ"
                
                # New filename should be the result of applying the pattern
                import re
                expected_new = re.sub(pattern, replacement, original)
                assert new == expected_new, f"New filename {new} doesn't match expected {expected_new}"
            
            # Verify files were not actually modified
            for filename in test_files:
                assert os.path.exists(os.path.join(tmpdir, filename)), f"File {filename} should not be modified"
        except ValueError:
            # Invalid regex patterns are acceptable
            pass


@given(
    num_files=st.integers(min_value=1, max_value=10)
)
def test_bulk_rename_completeness(num_files):
    """
    **Feature: lazy-automation-platform, Property 2: Bulk Rename Completeness**
    
    For any set of files matching a rename pattern, all matching files should be 
    renamed according to the pattern and an archive should be created.
    
    **Validates: Requirements 1.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        for i in range(num_files):
            with open(os.path.join(tmpdir, f"old_file{i}.txt"), "w") as f:
                f.write(f"content {i}")
        
        result = BulkRenamer.apply_rename(tmpdir, r"old_", "new_")
        
        # Verify all files were processed
        assert result.processed_count == num_files
        assert result.error_count == 0
        
        # Verify all files were renamed
        for filename in os.listdir(tmpdir):
            assert "new_" in filename


@given(
    num_duplicates=st.integers(min_value=2, max_value=10),
    content=st.binary(min_size=1, max_size=100),
    keep_first=st.booleans()
)
def test_duplicate_removal_preservation(num_duplicates, content, keep_first):
    """
    **Feature: lazy-automation-platform, Property 5: Duplicate Removal Preservation**
    
    For any set of duplicate files, removing duplicates should delete only the 
    duplicate copies while preserving at least one original file.
    
    **Validates: Requirements 1.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create duplicate files with the same content
        for i in range(num_duplicates):
            with open(os.path.join(tmpdir, f"dup{i}.txt"), "wb") as f:
                f.write(content)
        
        result = DuplicateCleaner.remove_duplicates(tmpdir, keep_first=keep_first)
        
        # Verify duplicates were removed
        assert result.processed_count == num_duplicates - 1, \
            f"Expected {num_duplicates - 1} duplicates removed, got {result.processed_count}"
        assert result.error_count == 0, \
            f"Expected no errors, got {result.error_count}"
        
        # Verify at least one file remains
        remaining_files = os.listdir(tmpdir)
        assert len(remaining_files) == 1, \
            f"Expected 1 file remaining, got {len(remaining_files)}"
        
        # Verify the remaining file has the correct content
        remaining_file = os.path.join(tmpdir, remaining_files[0])
        with open(remaining_file, "rb") as f:
            remaining_content = f.read()
        assert remaining_content == content, \
            f"Remaining file content doesn't match original content"

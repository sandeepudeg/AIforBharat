"""Tests for Web & Cloud Automation Module."""

import pytest
import tempfile
import os
import time
from pathlib import Path
from hypothesis import given, strategies as st
from src.web_cloud_automation import BulkDownloader, AutoFormFiller, CloudSyncCleanup
from src.data_models import FileOperationResult


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_downloads_dir(temp_dir):
    """Create a directory with sample downloaded files."""
    # Create various file types
    files = {
        "document.pdf": b"%PDF-1.4\nfake pdf",
        "image.png": b"\x89PNG\r\n\x1a\n",
        "video.mp4": b"fake video",
        "spreadsheet.xlsx": b"fake excel",
        "archive.zip": b"fake zip",
        "readme.txt": b"text content",
    }
    
    for filename, content in files.items():
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
    
    return temp_dir


@pytest.fixture
def sample_old_files_dir(temp_dir):
    """Create a directory with old and new files."""
    # Create new files
    for i in range(2):
        file_path = os.path.join(temp_dir, f"new_file{i}.txt")
        with open(file_path, "w") as f:
            f.write(f"new content {i}")
    
    # Create old files (modify their timestamps)
    for i in range(3):
        file_path = os.path.join(temp_dir, f"old_file{i}.txt")
        with open(file_path, "w") as f:
            f.write(f"old content {i}")
        
        # Set modification time to 10 days ago
        old_time = time.time() - (10 * 24 * 60 * 60)
        os.utime(file_path, (old_time, old_time))
    
    return temp_dir


# BulkDownloader Tests

def test_bulk_downloader_validate_urls_valid():
    """Test validating valid URLs."""
    urls = ["https://example.com/file.pdf", "https://example.com/image.png"]
    is_valid, error_msg = BulkDownloader.validate_urls(urls)
    
    assert is_valid is True
    assert error_msg == ""


def test_bulk_downloader_validate_urls_empty_list():
    """Test validating empty URL list."""
    urls = []
    is_valid, error_msg = BulkDownloader.validate_urls(urls)
    
    assert is_valid is False
    assert "empty" in error_msg.lower()


def test_bulk_downloader_validate_urls_invalid_format():
    """Test validating URLs with invalid format."""
    urls = ["not a url", "ftp://example.com/file"]
    is_valid, error_msg = BulkDownloader.validate_urls(urls)
    
    assert is_valid is False


def test_bulk_downloader_validate_urls_not_a_list():
    """Test that non-list input raises error."""
    with pytest.raises(ValueError):
        BulkDownloader.validate_urls("not a list")


def test_bulk_downloader_extract_filename_from_url():
    """Test extracting filename from URL."""
    url = "https://example.com/path/to/document.pdf"
    filename = BulkDownloader.extract_filename_from_url(url)
    
    assert filename == "document.pdf"


def test_bulk_downloader_extract_filename_no_path():
    """Test extracting filename from URL without path."""
    url = "https://example.com/"
    filename = BulkDownloader.extract_filename_from_url(url)
    
    assert isinstance(filename, str)
    assert len(filename) > 0


def test_bulk_downloader_extract_filename_invalid_url():
    """Test that invalid URL raises error."""
    with pytest.raises(ValueError):
        BulkDownloader.extract_filename_from_url("")


def test_bulk_downloader_organize_downloads(sample_downloads_dir):
    """Test organizing downloaded files by type."""
    urls = [
        "https://example.com/document.pdf",
        "https://example.com/image.png",
        "https://example.com/video.mp4",
    ]
    
    result = BulkDownloader.organize_downloads(sample_downloads_dir, urls)
    
    assert isinstance(result, FileOperationResult)
    assert result.success is True
    assert result.processed_count > 0
    
    # Verify subdirectories were created
    assert os.path.exists(os.path.join(sample_downloads_dir, "PDFs"))
    assert os.path.exists(os.path.join(sample_downloads_dir, "Images"))
    assert os.path.exists(os.path.join(sample_downloads_dir, "Videos"))


def test_bulk_downloader_organize_downloads_nonexistent_dir():
    """Test that nonexistent directory raises error."""
    urls = ["https://example.com/file.pdf"]
    
    with pytest.raises(FileNotFoundError):
        BulkDownloader.organize_downloads("/nonexistent/dir", urls)


def test_bulk_downloader_organize_downloads_invalid_urls(sample_downloads_dir):
    """Test that invalid URLs raise error."""
    urls = ["not a url"]
    
    with pytest.raises(ValueError):
        BulkDownloader.organize_downloads(sample_downloads_dir, urls)


# AutoFormFiller Tests

def test_auto_form_filler_create_profile():
    """Test creating a user profile."""
    filler = AutoFormFiller()
    profile_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234"
    }
    
    filler.create_profile("profile1", profile_data)
    
    retrieved = filler.get_profile("profile1")
    assert retrieved == profile_data


def test_auto_form_filler_create_profile_invalid_id():
    """Test that invalid profile ID raises error."""
    filler = AutoFormFiller()
    
    with pytest.raises(ValueError):
        filler.create_profile("", {"name": "John"})


def test_auto_form_filler_create_profile_empty_data():
    """Test that empty profile data raises error."""
    filler = AutoFormFiller()
    
    with pytest.raises(ValueError):
        filler.create_profile("profile1", {})


def test_auto_form_filler_populate_form():
    """Test populating form fields with profile data."""
    filler = AutoFormFiller()
    profile_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234"
    }
    filler.create_profile("profile1", profile_data)
    
    form_fields = {"name": "", "email": "", "phone": ""}
    populated = filler.populate_form("profile1", form_fields)
    
    assert populated["name"] == "John Doe"
    assert populated["email"] == "john@example.com"
    assert populated["phone"] == "555-1234"


def test_auto_form_filler_populate_form_case_insensitive():
    """Test that form population is case-insensitive."""
    filler = AutoFormFiller()
    profile_data = {"name": "John Doe", "email": "john@example.com"}
    filler.create_profile("profile1", profile_data)
    
    form_fields = {"Name": "", "EMAIL": ""}
    populated = filler.populate_form("profile1", form_fields)
    
    assert populated["Name"] == "John Doe"
    assert populated["EMAIL"] == "john@example.com"


def test_auto_form_filler_populate_form_nonexistent_profile():
    """Test that nonexistent profile raises error."""
    filler = AutoFormFiller()
    
    with pytest.raises(KeyError):
        filler.populate_form("nonexistent", {"name": ""})


def test_auto_form_filler_update_profile():
    """Test updating an existing profile."""
    filler = AutoFormFiller()
    profile_data = {"name": "John Doe", "email": "john@example.com"}
    filler.create_profile("profile1", profile_data)
    
    filler.update_profile("profile1", {"email": "newemail@example.com"})
    
    updated = filler.get_profile("profile1")
    assert updated["email"] == "newemail@example.com"
    assert updated["name"] == "John Doe"


def test_auto_form_filler_delete_profile():
    """Test deleting a profile."""
    filler = AutoFormFiller()
    filler.create_profile("profile1", {"name": "John"})
    
    result = filler.delete_profile("profile1")
    assert result is True
    assert filler.get_profile("profile1") is None


def test_auto_form_filler_delete_nonexistent_profile():
    """Test deleting a nonexistent profile."""
    filler = AutoFormFiller()
    
    result = filler.delete_profile("nonexistent")
    assert result is False


def test_auto_form_filler_get_all_profiles():
    """Test getting all profiles."""
    filler = AutoFormFiller()
    filler.create_profile("profile1", {"name": "John"})
    filler.create_profile("profile2", {"name": "Jane"})
    
    all_profiles = filler.get_all_profiles()
    
    assert len(all_profiles) == 2
    assert "profile1" in all_profiles
    assert "profile2" in all_profiles


def test_auto_form_filler_clear_profiles():
    """Test clearing all profiles."""
    filler = AutoFormFiller()
    filler.create_profile("profile1", {"name": "John"})
    filler.create_profile("profile2", {"name": "Jane"})
    
    filler.clear_profiles()
    
    all_profiles = filler.get_all_profiles()
    assert len(all_profiles) == 0


# CloudSyncCleanup Tests

def test_cloud_sync_cleanup_archive_old_files(sample_old_files_dir):
    """Test archiving old files."""
    cleanup = CloudSyncCleanup()
    
    # Archive files older than 5 days
    result = cleanup.archive_old_files(sample_old_files_dir, days_old=5)
    
    assert isinstance(result, FileOperationResult)
    assert result.success is True
    assert result.processed_count == 3  # 3 old files
    assert result.error_count == 0
    
    # Verify archive directory was created
    assert os.path.exists(os.path.join(sample_old_files_dir, "archive"))


def test_cloud_sync_cleanup_archive_old_files_no_old_files(temp_dir):
    """Test archiving when there are no old files."""
    # Create only new files
    for i in range(2):
        file_path = os.path.join(temp_dir, f"new_file{i}.txt")
        with open(file_path, "w") as f:
            f.write(f"new content {i}")
    
    cleanup = CloudSyncCleanup()
    result = cleanup.archive_old_files(temp_dir, days_old=5)
    
    assert result.processed_count == 0
    assert result.error_count == 0


def test_cloud_sync_cleanup_archive_old_files_invalid_days(temp_dir):
    """Test that invalid days_old raises error."""
    cleanup = CloudSyncCleanup()
    
    with pytest.raises(ValueError):
        cleanup.archive_old_files(temp_dir, days_old=-1)


def test_cloud_sync_cleanup_archive_old_files_nonexistent_dir():
    """Test that nonexistent directory raises error."""
    cleanup = CloudSyncCleanup()
    
    with pytest.raises(FileNotFoundError):
        cleanup.archive_old_files("/nonexistent/dir", days_old=5)


def test_cloud_sync_cleanup_get_archive_log(sample_old_files_dir):
    """Test getting the archive log."""
    cleanup = CloudSyncCleanup()
    cleanup.archive_old_files(sample_old_files_dir, days_old=5)
    
    log = cleanup.get_archive_log()
    
    assert isinstance(log, list)
    assert len(log) == 3


def test_cloud_sync_cleanup_get_archive_summary(sample_old_files_dir):
    """Test getting archive summary."""
    cleanup = CloudSyncCleanup()
    cleanup.archive_old_files(sample_old_files_dir, days_old=5)
    
    summary = cleanup.get_archive_summary()
    
    assert summary["total_archived"] == 3
    assert summary["successful"] == 3
    assert summary["failed"] == 0


def test_cloud_sync_cleanup_clear_archive_log(sample_old_files_dir):
    """Test clearing the archive log."""
    cleanup = CloudSyncCleanup()
    cleanup.archive_old_files(sample_old_files_dir, days_old=5)
    
    cleanup.clear_archive_log()
    
    log = cleanup.get_archive_log()
    assert len(log) == 0


def test_cloud_sync_cleanup_restore_from_archive(sample_old_files_dir):
    """Test restoring a file from archive."""
    cleanup = CloudSyncCleanup()
    cleanup.archive_old_files(sample_old_files_dir, days_old=5)
    
    archive_dir = os.path.join(sample_old_files_dir, "archive")
    restore_dir = os.path.join(sample_old_files_dir, "restored")
    os.makedirs(restore_dir, exist_ok=True)
    
    result = cleanup.restore_from_archive(archive_dir, "old_file0.txt", restore_dir)
    
    assert result is True
    assert os.path.exists(os.path.join(restore_dir, "old_file0.txt"))


def test_cloud_sync_cleanup_restore_nonexistent_file(sample_old_files_dir):
    """Test restoring a nonexistent file."""
    cleanup = CloudSyncCleanup()
    
    archive_dir = os.path.join(sample_old_files_dir, "archive")
    restore_dir = os.path.join(sample_old_files_dir, "restored")
    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(restore_dir, exist_ok=True)
    
    result = cleanup.restore_from_archive(archive_dir, "nonexistent.txt", restore_dir)
    
    assert result is False


# Property-Based Tests

@given(
    urls=st.lists(
        st.just("https://example.com/file.pdf") | st.just("https://example.com/image.png"),
        min_size=1,
        max_size=10
    )
)
def test_form_profile_auto_population(urls):
    """
    **Feature: lazy-automation-platform, Property 11: Form Profile Auto-Population**
    
    For any stored user profile and form fields, the auto-filler should correctly 
    match and populate form fields with corresponding profile data.
    
    **Validates: Requirements 4.2**
    """
    filler = AutoFormFiller()
    
    # Create a profile with test data
    profile_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-0000",
        "address": "123 Main St"
    }
    filler.create_profile("test_profile", profile_data)
    
    # Create form fields matching the profile
    form_fields = {
        "name": "",
        "email": "",
        "phone": "",
        "address": ""
    }
    
    # Populate the form
    populated = filler.populate_form("test_profile", form_fields)
    
    # Verify all fields were populated correctly
    for field_name in form_fields.keys():
        assert field_name in populated, f"Field {field_name} not in populated form"
        assert populated[field_name] == profile_data[field_name], \
            f"Field {field_name} not populated correctly"


@given(
    days_old=st.integers(min_value=1, max_value=30),
    num_files=st.integers(min_value=1, max_value=10)
)
def test_file_archive_integrity(days_old, num_files):
    """
    **Feature: lazy-automation-platform, Property 12: File Archive Integrity**
    
    For any file archived from storage, the archive operation should move the file 
    to an archive folder and create a corresponding log entry.
    
    **Validates: Requirements 4.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create old files
        for i in range(num_files):
            file_path = os.path.join(tmpdir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"content {i}")
            
            # Set modification time to be old
            old_time = time.time() - ((days_old + 1) * 24 * 60 * 60)
            os.utime(file_path, (old_time, old_time))
        
        cleanup = CloudSyncCleanup()
        result = cleanup.archive_old_files(tmpdir, days_old=days_old)
        
        # Verify files were archived
        assert result.processed_count == num_files, \
            f"Expected {num_files} files archived, got {result.processed_count}"
        assert result.error_count == 0, \
            f"Expected no errors, got {result.error_count}"
        
        # Verify archive directory exists
        archive_dir = os.path.join(tmpdir, "archive")
        assert os.path.exists(archive_dir), "Archive directory should exist"
        
        # Verify log entries were created
        log = cleanup.get_archive_log()
        assert len(log) == num_files, \
            f"Expected {num_files} log entries, got {len(log)}"
        
        # Verify each log entry has required fields
        for entry in log:
            assert "filename" in entry, "Log entry missing filename"
            assert "archived_at" in entry, "Log entry missing archived_at"
            assert "archive_path" in entry, "Log entry missing archive_path"
            assert "status" in entry, "Log entry missing status"
            assert entry["status"] == "success", "Log entry status should be success"

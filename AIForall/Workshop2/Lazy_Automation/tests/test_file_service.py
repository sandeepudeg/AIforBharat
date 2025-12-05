"""Tests for FileService."""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st
from src.file_service import FileService


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    files = {}
    
    # Create a text file
    text_file = os.path.join(temp_dir, "sample.txt")
    with open(text_file, "w") as f:
        f.write("This is a sample text file")
    files["text"] = text_file
    
    # Create a PDF file (fake)
    pdf_file = os.path.join(temp_dir, "sample.pdf")
    with open(pdf_file, "wb") as f:
        f.write(b"%PDF-1.4\n%fake pdf content")
    files["pdf"] = pdf_file
    
    # Create an image file (fake)
    image_file = os.path.join(temp_dir, "sample.png")
    with open(image_file, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
    files["image"] = image_file
    
    # Create a video file (fake)
    video_file = os.path.join(temp_dir, "sample.mp4")
    with open(video_file, "wb") as f:
        f.write(b"fake video content")
    files["video"] = video_file
    
    # Create an archive file (fake)
    archive_file = os.path.join(temp_dir, "sample.zip")
    with open(archive_file, "wb") as f:
        f.write(b"PK\x03\x04")
    files["archive"] = archive_file
    
    return files


def test_compute_file_hash_basic(sample_files):
    """Test computing hash of a file."""
    hash_value = FileService.compute_file_hash(sample_files["text"])
    
    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA-256 produces 64 hex characters


def test_compute_file_hash_consistency(sample_files):
    """Test that computing hash twice produces same result."""
    hash1 = FileService.compute_file_hash(sample_files["text"])
    hash2 = FileService.compute_file_hash(sample_files["text"])
    
    assert hash1 == hash2


def test_compute_file_hash_different_files(sample_files):
    """Test that different files produce different hashes."""
    hash1 = FileService.compute_file_hash(sample_files["text"])
    hash2 = FileService.compute_file_hash(sample_files["pdf"])
    
    assert hash1 != hash2


def test_compute_file_hash_nonexistent_file():
    """Test that computing hash of nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        FileService.compute_file_hash("/nonexistent/file.txt")


def test_detect_file_type_pdf(sample_files):
    """Test detecting PDF file type."""
    file_type = FileService.detect_file_type(sample_files["pdf"])
    assert file_type == "pdf"


def test_detect_file_type_image(sample_files):
    """Test detecting image file type."""
    file_type = FileService.detect_file_type(sample_files["image"])
    assert file_type == "image"


def test_detect_file_type_video(sample_files):
    """Test detecting video file type."""
    file_type = FileService.detect_file_type(sample_files["video"])
    assert file_type == "video"


def test_detect_file_type_archive(sample_files):
    """Test detecting archive file type."""
    file_type = FileService.detect_file_type(sample_files["archive"])
    assert file_type == "archive"


def test_detect_file_type_text(sample_files):
    """Test detecting text file type."""
    file_type = FileService.detect_file_type(sample_files["text"])
    assert file_type == "document"


def test_detect_file_type_unknown(temp_dir):
    """Test detecting unknown file type."""
    unknown_file = os.path.join(temp_dir, "sample.xyz")
    with open(unknown_file, "w") as f:
        f.write("unknown content")
    
    file_type = FileService.detect_file_type(unknown_file)
    assert file_type == "unknown"


def test_detect_file_type_nonexistent_file():
    """Test that detecting type of nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        FileService.detect_file_type("/nonexistent/file.txt")


def test_move_file_basic(temp_dir, sample_files):
    """Test moving a file."""
    source = sample_files["text"]
    destination = os.path.join(temp_dir, "moved", "sample.txt")
    
    result = FileService.move_file(source, destination)
    
    assert result is True
    assert os.path.exists(destination)
    assert not os.path.exists(source)


def test_move_file_creates_destination_directory(temp_dir, sample_files):
    """Test that move_file creates destination directory if needed."""
    source = sample_files["text"]
    destination = os.path.join(temp_dir, "new", "nested", "dir", "sample.txt")
    
    FileService.move_file(source, destination)
    
    assert os.path.exists(destination)
    assert os.path.isdir(os.path.dirname(destination))


def test_move_file_nonexistent_source(temp_dir):
    """Test that moving nonexistent file raises error."""
    with pytest.raises(FileNotFoundError):
        FileService.move_file("/nonexistent/file.txt", os.path.join(temp_dir, "dest.txt"))


def test_find_duplicates_no_duplicates(temp_dir):
    """Test finding duplicates when there are none."""
    # Create unique files
    for i in range(3):
        with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
            f.write(f"unique content {i}")
    
    duplicates = FileService.find_duplicates(temp_dir)
    
    assert duplicates == []


def test_find_duplicates_with_duplicates(temp_dir):
    """Test finding duplicate files."""
    # Create duplicate files
    content = "duplicate content"
    for i in range(3):
        with open(os.path.join(temp_dir, f"file{i}.txt"), "w") as f:
            f.write(content)
    
    duplicates = FileService.find_duplicates(temp_dir)
    
    assert len(duplicates) == 1
    assert len(duplicates[0]) == 3


def test_find_duplicates_mixed(temp_dir):
    """Test finding duplicates with mixed unique and duplicate files."""
    # Create unique files
    with open(os.path.join(temp_dir, "unique1.txt"), "w") as f:
        f.write("unique1")
    with open(os.path.join(temp_dir, "unique2.txt"), "w") as f:
        f.write("unique2")
    
    # Create duplicate files
    for i in range(2):
        with open(os.path.join(temp_dir, f"dup{i}.txt"), "w") as f:
            f.write("duplicate")
    
    duplicates = FileService.find_duplicates(temp_dir)
    
    assert len(duplicates) == 1
    assert len(duplicates[0]) == 2


def test_find_duplicates_nonexistent_directory():
    """Test that finding duplicates in nonexistent directory raises error."""
    with pytest.raises(FileNotFoundError):
        FileService.find_duplicates("/nonexistent/directory")


def test_find_duplicates_not_a_directory(temp_dir):
    """Test that finding duplicates on a file raises error."""
    file_path = os.path.join(temp_dir, "file.txt")
    with open(file_path, "w") as f:
        f.write("content")
    
    with pytest.raises(NotADirectoryError):
        FileService.find_duplicates(file_path)


def test_find_duplicates_nested_directories(temp_dir):
    """Test finding duplicates in nested directories."""
    # Create nested structure
    nested_dir = os.path.join(temp_dir, "nested", "dir")
    os.makedirs(nested_dir, exist_ok=True)
    
    # Create duplicate files in different directories
    content = "duplicate"
    with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
        f.write(content)
    with open(os.path.join(nested_dir, "file2.txt"), "w") as f:
        f.write(content)
    
    duplicates = FileService.find_duplicates(temp_dir)
    
    assert len(duplicates) == 1
    assert len(duplicates[0]) == 2


# Property-Based Tests

@given(
    content=st.binary(min_size=1, max_size=1000)
)
def test_file_type_detection_accuracy(content):
    """
    **Feature: lazy-automation-platform, Property 3: File Type Detection Accuracy**
    
    For any file with a known extension, the file type detection should correctly 
    classify it into the appropriate category (PDF, image, video, document, archive).
    
    **Validates: Requirements 1.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test with known extensions
        test_cases = [
            ("test.pdf", "pdf"),
            ("test.png", "image"),
            ("test.mp4", "video"),
            ("test.zip", "archive"),
            ("test.txt", "document"),
        ]
        
        for filename, expected_type in test_cases:
            file_path = os.path.join(tmpdir, filename)
            with open(file_path, "wb") as f:
                f.write(content)
            
            detected_type = FileService.detect_file_type(file_path)
            assert detected_type == expected_type, f"Expected {expected_type}, got {detected_type} for {filename}"


@given(
    content1=st.binary(min_size=1, max_size=500),
    content2=st.binary(min_size=1, max_size=500)
)
def test_duplicate_detection_completeness(content1, content2):
    """
    **Feature: lazy-automation-platform, Property 4: Duplicate Detection Completeness**
    
    For any set of files where some are duplicates (identical content), the duplicate 
    cleaner should identify all duplicate pairs.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with content1 (duplicates)
        for i in range(2):
            with open(os.path.join(tmpdir, f"dup{i}.bin"), "wb") as f:
                f.write(content1)
        
        # Create files with content2 (unique)
        with open(os.path.join(tmpdir, "unique.bin"), "wb") as f:
            f.write(content2)
        
        duplicates = FileService.find_duplicates(tmpdir)
        
        # Should find exactly one group of duplicates (the two files with content1)
        # Only if content1 != content2
        if content1 != content2:
            assert len(duplicates) == 1
            assert len(duplicates[0]) == 2
        else:
            # If content1 == content2, all 3 files are duplicates
            assert len(duplicates) == 1
            assert len(duplicates[0]) == 3

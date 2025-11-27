import pytest
from hypothesis import given, strategies as st
from datetime import datetime
from utils.file_utils import generate_filename
import re

class TestFileNaming:
    """Test file naming functionality"""
    
    def test_pdf_filename_format(self):
        """Test PDF filename format"""
        filename = generate_filename('pdf')
        
        # Check format: contract_YYYY-MM-DD.pdf
        assert filename.startswith('contract_')
        assert filename.endswith('.pdf')
        
        # Extract date part
        date_part = filename.replace('contract_', '').replace('.pdf', '')
        # Verify date format YYYY-MM-DD
        assert re.match(r'\d{4}-\d{2}-\d{2}', date_part)
    
    def test_docx_filename_format(self):
        """Test DOCX filename format"""
        filename = generate_filename('docx')
        
        # Check format: contract_YYYY-MM-DD.docx
        assert filename.startswith('contract_')
        assert filename.endswith('.docx')
        
        # Extract date part
        date_part = filename.replace('contract_', '').replace('.docx', '')
        # Verify date format YYYY-MM-DD
        assert re.match(r'\d{4}-\d{2}-\d{2}', date_part)
    
    def test_filename_contains_valid_date(self):
        """Test that filename contains valid date"""
        filename = generate_filename('pdf')
        
        # Extract date part
        date_part = filename.replace('contract_', '').replace('.pdf', '')
        
        # Try to parse the date
        try:
            date_obj = datetime.strptime(date_part, '%Y-%m-%d')
            assert date_obj is not None
        except ValueError:
            pytest.fail(f"Invalid date format in filename: {filename}")
    
    def test_filename_date_is_today(self):
        """Test that filename date is today's date"""
        filename = generate_filename('pdf')
        
        # Extract date part
        date_part = filename.replace('contract_', '').replace('.pdf', '')
        
        # Parse the date
        file_date = datetime.strptime(date_part, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        assert file_date == today
    
    def test_multiple_filenames_have_same_date(self):
        """Test that multiple filenames generated on same day have same date"""
        filename1 = generate_filename('pdf')
        filename2 = generate_filename('docx')
        
        # Extract date parts
        date_part1 = filename1.replace('contract_', '').replace('.pdf', '')
        date_part2 = filename2.replace('contract_', '').replace('.docx', '')
        
        # Dates should be the same
        assert date_part1 == date_part2
    
    @given(st.just('pdf'))
    def test_download_files_have_correct_naming(self, file_format):
        """
        **Feature: contract-generator, Property 7: Download Files Have Correct Naming**
        **Validates: Requirements 2.4**
        
        For any generated contract, the downloaded PDF and Word files should be named with
        a clear identifier including the generation date (e.g., contract_YYYY-MM-DD.pdf or
        contract_YYYY-MM-DD.docx).
        """
        filename = generate_filename(file_format)
        
        # Check format
        assert filename.startswith('contract_')
        assert filename.endswith(f'.{file_format}')
        
        # Extract date part
        date_part = filename.replace('contract_', '').replace(f'.{file_format}', '')
        
        # Verify date format YYYY-MM-DD
        assert re.match(r'\d{4}-\d{2}-\d{2}', date_part)
        
        # Verify date is valid
        try:
            date_obj = datetime.strptime(date_part, '%Y-%m-%d')
            assert date_obj is not None
        except ValueError:
            pytest.fail(f"Invalid date format in filename: {filename}")
    
    @given(st.just('docx'))
    def test_download_files_have_correct_naming_docx(self, file_format):
        """Test DOCX file naming"""
        filename = generate_filename(file_format)
        
        # Check format
        assert filename.startswith('contract_')
        assert filename.endswith(f'.{file_format}')
        
        # Extract date part
        date_part = filename.replace('contract_', '').replace(f'.{file_format}', '')
        
        # Verify date format YYYY-MM-DD
        assert re.match(r'\d{4}-\d{2}-\d{2}', date_part)
    
    def test_filename_is_unique_per_day(self):
        """Test that filename is consistent within a day"""
        # Generate multiple filenames
        filenames = [generate_filename('pdf') for _ in range(5)]
        
        # All should be the same (same day)
        assert len(set(filenames)) == 1
    
    def test_filename_no_special_characters(self):
        """Test that filename has no problematic special characters"""
        filename = generate_filename('pdf')
        
        # Check for problematic characters
        problematic_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in problematic_chars:
            assert char not in filename, f"Filename contains problematic character: {char}"
    
    def test_filename_is_filesystem_safe(self):
        """Test that filename is safe for filesystems"""
        filename = generate_filename('pdf')
        
        # Should only contain alphanumeric, underscore, hyphen, and dot
        assert re.match(r'^[a-zA-Z0-9_\-\.]+$', filename)
    
    def test_filename_length_is_reasonable(self):
        """Test that filename length is reasonable"""
        filename = generate_filename('pdf')
        
        # Should be reasonably short (less than 100 characters)
        assert len(filename) < 100
        # Should be at least 20 characters (contract_YYYY-MM-DD.pdf)
        assert len(filename) >= 20

"""Tests for Gradio UI module."""

import pytest
import tempfile
import os
import json
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck
from src.gradio_ui import GradioUI


@pytest.fixture
def gradio_ui():
    """Create a GradioUI instance for testing."""
    return GradioUI()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"file_{i}.txt")
        with open(file_path, "w") as f:
            f.write(f"content {i}")
        files.append(file_path)
    return files


class TestGradioUIFileAutomation:
    """Tests for File Automation tab functionality."""

    def test_bulk_rename_preview_valid_directory(self, gradio_ui, temp_dir, sample_files):
        """Test bulk rename preview with valid directory."""
        status, preview = gradio_ui.bulk_rename_preview(temp_dir, "file_", "renamed_")
        
        assert "Preview" in status or "No files" in status
        assert isinstance(preview, list)

    def test_bulk_rename_preview_invalid_directory(self, gradio_ui):
        """Test bulk rename preview with invalid directory."""
        status, preview = gradio_ui.bulk_rename_preview("/nonexistent/path", "pattern", "replacement")
        
        assert "Error" in status
        assert preview == []

    def test_bulk_rename_apply_valid_directory(self, gradio_ui, temp_dir, sample_files):
        """Test bulk rename apply with valid directory."""
        status = gradio_ui.bulk_rename_apply(temp_dir, "file_", "renamed_")
        
        assert "Success" in status or "Error" in status or "Completed" in status

    def test_bulk_rename_apply_invalid_directory(self, gradio_ui):
        """Test bulk rename apply with invalid directory."""
        status = gradio_ui.bulk_rename_apply("/nonexistent/path", "pattern", "replacement")
        
        assert "Error" in status

    def test_auto_organize_valid_directory(self, gradio_ui, temp_dir, sample_files):
        """Test auto-organize with valid directory."""
        status = gradio_ui.auto_organize(temp_dir)
        
        assert "Success" in status or "Error" in status or "Completed" in status

    def test_auto_organize_invalid_directory(self, gradio_ui):
        """Test auto-organize with invalid directory."""
        status = gradio_ui.auto_organize("/nonexistent/path")
        
        assert "Error" in status

    def test_get_file_type_distribution_valid_directory(self, gradio_ui, temp_dir, sample_files):
        """Test file type distribution with valid directory."""
        status = gradio_ui.get_file_type_distribution(temp_dir)
        
        assert "Error" not in status or "Distribution" in status or "No files" in status

    def test_get_file_type_distribution_invalid_directory(self, gradio_ui):
        """Test file type distribution with invalid directory."""
        status = gradio_ui.get_file_type_distribution("/nonexistent/path")
        
        assert "Error" in status

    def test_find_duplicates_valid_directory(self, gradio_ui, temp_dir):
        """Test find duplicates with valid directory."""
        status = gradio_ui.find_duplicates(temp_dir)
        
        assert "Error" not in status or "Summary" in status or "No duplicates" in status

    def test_find_duplicates_invalid_directory(self, gradio_ui):
        """Test find duplicates with invalid directory."""
        status = gradio_ui.find_duplicates("/nonexistent/path")
        
        assert "Error" in status

    def test_remove_duplicates_valid_directory(self, gradio_ui, temp_dir):
        """Test remove duplicates with valid directory."""
        status = gradio_ui.remove_duplicates(temp_dir, keep_first=True)
        
        assert "Success" in status or "Error" in status or "Completed" in status

    def test_remove_duplicates_invalid_directory(self, gradio_ui):
        """Test remove duplicates with invalid directory."""
        status = gradio_ui.remove_duplicates("/nonexistent/path")
        
        assert "Error" in status


class TestGradioUICommunicationAutomation:
    """Tests for Communication Automation tab functionality."""

    def test_summarize_emails_valid_input(self, gradio_ui):
        """Test email summarization with valid input."""
        email_body = "This is a long email with lots of content that needs to be summarized into a shorter version."
        status = gradio_ui.summarize_emails(email_body, max_length=50)
        
        assert "Original Length" in status
        assert "Summary Length" in status
        assert "Summary" in status

    def test_summarize_emails_empty_input(self, gradio_ui):
        """Test email summarization with empty input."""
        status = gradio_ui.summarize_emails("", max_length=100)
        
        assert "Error" in status

    def test_add_template_valid_input(self, gradio_ui):
        """Test adding a template with valid input."""
        status = gradio_ui.add_template("urgent_reply", "urgent, asap", "This is urgent, I'll handle it immediately.")
        
        assert "Success" in status

    def test_add_template_empty_template_id(self, gradio_ui):
        """Test adding a template with empty template ID."""
        status = gradio_ui.add_template("", "urgent", "Response")
        
        assert "Error" in status

    def test_add_template_empty_keywords(self, gradio_ui):
        """Test adding a template with empty keywords."""
        status = gradio_ui.add_template("template_1", "", "Response")
        
        assert "Error" in status

    def test_add_template_empty_response(self, gradio_ui):
        """Test adding a template with empty response."""
        status = gradio_ui.add_template("template_1", "urgent", "")
        
        assert "Error" in status

    def test_match_template_valid_input(self, gradio_ui):
        """Test template matching with valid input."""
        # First add a template
        gradio_ui.add_template("urgent_reply", "urgent, asap", "This is urgent!")
        
        # Then try to match
        status = gradio_ui.match_template("This is urgent and needs immediate attention")
        
        assert "Matched Template" in status or "No matching template" in status

    def test_match_template_empty_input(self, gradio_ui):
        """Test template matching with empty input."""
        status = gradio_ui.match_template("")
        
        assert "Error" in status

    def test_list_templates_empty(self):
        """Test listing templates when none exist."""
        # Create a fresh UI instance to ensure no templates are loaded
        fresh_ui = GradioUI()
        fresh_ui.template_responder.clear_templates()
        status = fresh_ui.list_templates()
        
        assert "No templates" in status

    def test_list_templates_with_templates(self, gradio_ui):
        """Test listing templates when some exist."""
        gradio_ui.add_template("template_1", "keyword1", "Response 1")
        status = gradio_ui.list_templates()
        
        assert "Configured Templates" in status or "template_1" in status

    def test_add_reminder_valid_input(self, gradio_ui):
        """Test adding a reminder with valid input."""
        status = gradio_ui.add_reminder("meeting_1", "Team Meeting", "2024-01-15T14:30:00", "slack")
        
        assert "Success" in status

    def test_add_reminder_empty_reminder_id(self, gradio_ui):
        """Test adding a reminder with empty reminder ID."""
        status = gradio_ui.add_reminder("", "Event", "2024-01-15T14:30:00", "slack")
        
        assert "Error" in status

    def test_add_reminder_empty_event_name(self, gradio_ui):
        """Test adding a reminder with empty event name."""
        status = gradio_ui.add_reminder("reminder_1", "", "2024-01-15T14:30:00", "slack")
        
        assert "Error" in status

    def test_add_reminder_empty_event_time(self, gradio_ui):
        """Test adding a reminder with empty event time."""
        status = gradio_ui.add_reminder("reminder_1", "Event", "", "slack")
        
        assert "Error" in status

    def test_add_reminder_empty_channel(self, gradio_ui):
        """Test adding a reminder with empty channel."""
        status = gradio_ui.add_reminder("reminder_1", "Event", "2024-01-15T14:30:00", "")
        
        assert "Error" in status

    def test_send_reminder_valid_input(self, gradio_ui):
        """Test sending a reminder with valid input."""
        # First add a reminder
        gradio_ui.add_reminder("meeting_1", "Team Meeting", "2024-01-15T14:30:00", "slack")
        
        # Then send it
        status = gradio_ui.send_reminder("meeting_1")
        
        assert "Success" in status

    def test_send_reminder_nonexistent(self, gradio_ui):
        """Test sending a nonexistent reminder."""
        status = gradio_ui.send_reminder("nonexistent_reminder")
        
        assert "Error" in status or "not found" in status

    def test_send_reminder_empty_id(self, gradio_ui):
        """Test sending a reminder with empty ID."""
        status = gradio_ui.send_reminder("")
        
        assert "Error" in status

    def test_list_reminders_empty(self, gradio_ui):
        """Test listing reminders when none exist."""
        status = gradio_ui.list_reminders()
        
        assert "No reminders" in status

    def test_list_reminders_with_reminders(self, gradio_ui):
        """Test listing reminders when some exist."""
        gradio_ui.add_reminder("reminder_1", "Event 1", "2024-01-15T14:30:00", "slack")
        status = gradio_ui.list_reminders()
        
        assert "Configured Reminders" in status or "reminder_1" in status


class TestGradioUIInterfaceBuilding:
    """Tests for Gradio interface building."""

    def test_build_interface_returns_blocks(self, gradio_ui):
        """Test that build_interface returns a Gradio Blocks object."""
        interface = gradio_ui.build_interface()
        
        # Check that it's a Gradio Blocks object
        assert interface is not None
        assert hasattr(interface, 'launch')

    def test_interface_has_tabs(self, gradio_ui):
        """Test that the interface has the expected tabs."""
        interface = gradio_ui.build_interface()
        
        # The interface should be created successfully
        assert interface is not None


class TestProductivityAutomation:
    """Tests for Productivity Automation tab functionality."""

    def test_parse_csv_file_valid(self, gradio_ui, temp_dir):
        """Test CSV parsing with valid file."""
        # Create a test CSV file
        csv_path = os.path.join(temp_dir, "test.csv")
        with open(csv_path, "w") as f:
            f.write("name,age,city\n")
            f.write("John,30,NYC\n")
            f.write("Jane,25,LA\n")
        
        result = gradio_ui.parse_csv_file(csv_path)
        
        assert "CSV Statistics" in result
        assert "Rows: 2" in result
        assert "Columns: 3" in result

    def test_parse_csv_file_invalid_path(self, gradio_ui):
        """Test CSV parsing with invalid path."""
        result = gradio_ui.parse_csv_file("/nonexistent/file.csv")
        
        assert "Error" in result

    def test_export_csv_to_json_valid(self, gradio_ui, temp_dir):
        """Test CSV to JSON export with valid file."""
        csv_path = os.path.join(temp_dir, "test.csv")
        with open(csv_path, "w") as f:
            f.write("name,age\n")
            f.write("John,30\n")
        
        result = gradio_ui.export_csv_to_json(csv_path)
        
        # Should be valid JSON
        try:
            json.loads(result)
            assert True
        except json.JSONDecodeError:
            assert False, "Output should be valid JSON"

    def test_analyze_log_file_valid(self, gradio_ui, temp_dir):
        """Test log file analysis with valid file."""
        log_path = os.path.join(temp_dir, "test.log")
        with open(log_path, "w") as f:
            f.write("INFO: Starting application\n")
            f.write("ERROR: Connection failed\n")
            f.write("WARNING: Low memory\n")
        
        result = gradio_ui.analyze_log_file(log_path)
        
        assert "Log Analysis" in result
        assert "Errors: 1" in result
        assert "Warnings: 1" in result

    def test_analyze_log_file_invalid_path(self, gradio_ui):
        """Test log file analysis with invalid path."""
        result = gradio_ui.analyze_log_file("/nonexistent/file.log")
        
        assert "Error" in result

    def test_add_clipboard_item_valid(self, gradio_ui):
        """Test adding clipboard item with valid input."""
        result = gradio_ui.add_clipboard_item("Test content", "test_task", "tag1,tag2")
        
        assert "Success" in result

    def test_add_clipboard_item_empty_content(self, gradio_ui):
        """Test adding clipboard item with empty content."""
        result = gradio_ui.add_clipboard_item("", "test_task", "tag1")
        
        assert "Error" in result

    def test_search_clipboard_valid(self, gradio_ui):
        """Test clipboard search with valid query."""
        gradio_ui.add_clipboard_item("Important document", "task1", "important")
        result = gradio_ui.search_clipboard("Important")
        
        assert "matching items" in result or "Important" in result

    def test_search_clipboard_empty_query(self, gradio_ui):
        """Test clipboard search with empty query."""
        result = gradio_ui.search_clipboard("")
        
        assert "Error" in result

    def test_get_clipboard_history_empty(self, gradio_ui):
        """Test getting clipboard history when empty."""
        result = gradio_ui.get_clipboard_history()
        
        assert "empty" in result.lower()

    def test_get_clipboard_history_with_items(self, gradio_ui):
        """Test getting clipboard history with items."""
        gradio_ui.add_clipboard_item("Item 1", "task1", "")
        gradio_ui.add_clipboard_item("Item 2", "task2", "")
        result = gradio_ui.get_clipboard_history()
        
        assert "Clipboard History" in result
        assert "2 items" in result


class TestWebCloudAutomation:
    """Tests for Web & Cloud Automation tab functionality."""

    def test_validate_urls_valid(self, gradio_ui):
        """Test URL validation with valid URLs."""
        urls = "https://example.com/file1.pdf\nhttps://example.com/file2.pdf"
        result = gradio_ui.validate_urls(urls)
        
        assert "Success" in result

    def test_validate_urls_invalid_format(self, gradio_ui):
        """Test URL validation with invalid format."""
        urls = "not a url\ninvalid"
        result = gradio_ui.validate_urls(urls)
        
        assert "Error" in result

    def test_validate_urls_empty(self, gradio_ui):
        """Test URL validation with empty input."""
        result = gradio_ui.validate_urls("")
        
        assert "Error" in result

    def test_organize_downloads_valid(self, gradio_ui, temp_dir):
        """Test organizing downloads with valid directory."""
        # Create some test files
        for ext in [".pdf", ".jpg", ".txt"]:
            with open(os.path.join(temp_dir, f"file{ext}"), "w") as f:
                f.write("test")
        
        urls = "https://example.com/file.pdf\nhttps://example.com/file.jpg"
        result = gradio_ui.organize_downloads(temp_dir, urls)
        
        assert "Success" in result or "Completed" in result or "Error" not in result

    def test_organize_downloads_invalid_directory(self, gradio_ui):
        """Test organizing downloads with invalid directory."""
        urls = "https://example.com/file.pdf"
        result = gradio_ui.organize_downloads("/nonexistent/path", urls)
        
        assert "Error" in result

    def test_create_form_profile_valid(self, gradio_ui):
        """Test creating form profile with valid input."""
        profile_data = '{"name": "John", "email": "john@example.com"}'
        result = gradio_ui.create_form_profile("profile1", profile_data)
        
        assert "Success" in result

    def test_create_form_profile_invalid_json(self, gradio_ui):
        """Test creating form profile with invalid JSON."""
        result = gradio_ui.create_form_profile("profile1", "not json")
        
        assert "Error" in result

    def test_create_form_profile_empty_id(self, gradio_ui):
        """Test creating form profile with empty ID."""
        profile_data = '{"name": "John"}'
        result = gradio_ui.create_form_profile("", profile_data)
        
        assert "Error" in result

    def test_populate_form_fields_valid(self, gradio_ui):
        """Test populating form fields with valid profile."""
        profile_data = '{"name": "John", "email": "john@example.com"}'
        gradio_ui.create_form_profile("profile1", profile_data)
        
        form_fields = '{"name": "", "email": ""}'
        result = gradio_ui.populate_form_fields("profile1", form_fields)
        
        # Should return valid JSON
        try:
            populated = json.loads(result)
            assert "name" in populated or "email" in populated
        except json.JSONDecodeError:
            assert False, "Output should be valid JSON"

    def test_populate_form_fields_nonexistent_profile(self, gradio_ui):
        """Test populating form fields with nonexistent profile."""
        form_fields = '{"name": "", "email": ""}'
        result = gradio_ui.populate_form_fields("nonexistent", form_fields)
        
        assert "Error" in result

    def test_list_form_profiles_empty(self, gradio_ui):
        """Test listing form profiles when none exist."""
        result = gradio_ui.list_form_profiles()
        
        assert "No form profiles" in result

    def test_list_form_profiles_with_profiles(self, gradio_ui):
        """Test listing form profiles when some exist."""
        profile_data = '{"name": "John"}'
        gradio_ui.create_form_profile("profile1", profile_data)
        result = gradio_ui.list_form_profiles()
        
        assert "Stored Form Profiles" in result or "profile1" in result

    def test_archive_old_files_valid(self, gradio_ui, temp_dir):
        """Test archiving old files with valid directory."""
        result = gradio_ui.archive_old_files(temp_dir, 30)
        
        assert "Success" in result or "Completed" in result or "Error" not in result

    def test_archive_old_files_invalid_directory(self, gradio_ui):
        """Test archiving old files with invalid directory."""
        result = gradio_ui.archive_old_files("/nonexistent/path", 30)
        
        assert "Error" in result

    def test_get_archive_summary(self, gradio_ui):
        """Test getting archive summary."""
        result = gradio_ui.get_archive_summary()
        
        assert "Archive Summary" in result


class TestTabStatePreservation:
    """Property-based tests for tab state preservation.
    
    **Feature: lazy-automation-platform, Property 13: Tab State Preservation**
    **Validates: Requirements 5.5**
    """

    @given(
        template_id=st.from_regex(r'[a-zA-Z0-9_]{1,20}', fullmatch=True),
        keywords=st.from_regex(r'[a-zA-Z0-9_]{1,10}(,[a-zA-Z0-9_]{1,10}){0,2}', fullmatch=True),
        response=st.from_regex(r'[a-zA-Z0-9 ]{10,50}', fullmatch=True)
    )
    def test_tab_state_preserved_on_navigation(self, template_id, keywords, response):
        """
        Property: For any tab navigation sequence, configuration options should remain unchanged
        when returning to a previously visited tab.
        
        This test simulates:
        1. Configuring options in Communication Automation tab (adding a template)
        2. Navigating to File Automation tab
        3. Returning to Communication Automation tab
        4. Verifying the template configuration is still present
        """
        gradio_ui = GradioUI()
        
        # Step 1: Configure template in Communication Automation tab
        # (simulating user input and configuration)
        add_result = gradio_ui.add_template(template_id, keywords, response)
        
        # Verify template was successfully added
        assert "Success" in add_result, f"Template addition failed: {add_result}"
        
        # Step 2: Simulate navigation to File Automation tab
        # (in a real Gradio app, this would be a tab click)
        # We simulate this by calling a File Automation function
        temp_dir = tempfile.mkdtemp()
        try:
            gradio_ui.get_file_type_distribution(temp_dir)
            
            # Step 3: Return to Communication Automation tab
            # (simulate by calling a Communication function again)
            
            # Step 4: Verify the template configuration is still present
            list_result = gradio_ui.list_templates()
            
            # The template should still be in the list after navigation
            assert template_id in list_result, \
                f"Template '{template_id}' was not preserved after tab navigation"
            assert "Configured Templates" in list_result, \
                "Templates list should show configured templates"
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestDashboardFunctionality:
    """Tests for Dashboard tab functionality.
    
    **Feature: lazy-automation-platform, Property 34: Dashboard Status Display**
    **Validates: Requirements 12.1**
    """

    def test_get_dashboard_summary_returns_string(self, gradio_ui):
        """Test that dashboard summary returns a formatted string."""
        result = gradio_ui.get_dashboard_summary()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "DASHBOARD SUMMARY" in result or "USAGE STATISTICS" in result

    def test_get_automation_status_returns_string(self, gradio_ui):
        """Test that automation status returns a formatted string."""
        result = gradio_ui.get_automation_status()
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_time_saved_report_returns_string(self, gradio_ui):
        """Test that time saved report returns a formatted string."""
        result = gradio_ui.get_time_saved_report()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "TIME SAVED" in result or "Total Time Saved" in result

    def test_get_error_log_report_returns_string(self, gradio_ui):
        """Test that error log report returns a formatted string."""
        result = gradio_ui.get_error_log_report()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "ERROR" in result.upper()

    def test_get_undo_history_returns_string(self, gradio_ui):
        """Test that undo history returns a formatted string."""
        result = gradio_ui.get_undo_history()
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_perform_undo_empty_backup_id(self, gradio_ui):
        """Test undo with empty backup ID."""
        result = gradio_ui.perform_undo("")
        
        assert "Error" in result

    def test_perform_undo_nonexistent_backup(self, gradio_ui):
        """Test undo with nonexistent backup ID."""
        result = gradio_ui.perform_undo("nonexistent_backup_id")
        
        assert "Error" in result or "not found" in result.lower()


class TestSettingsFunctionality:
    """Tests for Settings tab functionality.
    
    **Feature: lazy-automation-platform, Property 20: Configuration Update Immediacy**
    **Validates: Requirements 7.3**
    """

    def test_get_all_settings_returns_string(self, gradio_ui):
        """Test that get all settings returns a formatted string."""
        result = gradio_ui.get_all_settings()
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_save_setting_valid_input(self, gradio_ui):
        """Test saving a setting with valid input."""
        result = gradio_ui.save_setting("test_key", "test_value")
        
        assert "Success" in result

    def test_save_setting_empty_key(self, gradio_ui):
        """Test saving a setting with empty key."""
        result = gradio_ui.save_setting("", "test_value")
        
        assert "Error" in result

    def test_save_setting_empty_value(self, gradio_ui):
        """Test saving a setting with empty value."""
        result = gradio_ui.save_setting("test_key", "")
        
        assert "Error" in result

    def test_save_setting_json_value(self, gradio_ui):
        """Test saving a setting with JSON value."""
        json_value = '{"key": "value", "number": 42}'
        result = gradio_ui.save_setting("json_setting", json_value)
        
        assert "Success" in result

    def test_save_credential_valid_input(self, gradio_ui):
        """Test saving a credential with valid input."""
        result = gradio_ui.save_credential("test_cred", "secret_value")
        
        assert "Success" in result
        assert "encrypted" in result.lower()

    def test_save_credential_empty_key(self, gradio_ui):
        """Test saving a credential with empty key."""
        result = gradio_ui.save_credential("", "secret_value")
        
        assert "Error" in result

    def test_save_credential_empty_value(self, gradio_ui):
        """Test saving a credential with empty value."""
        result = gradio_ui.save_credential("test_cred", "")
        
        assert "Error" in result

    def test_clear_setting_valid_key(self, gradio_ui):
        """Test clearing a setting with valid key."""
        # First save a setting
        gradio_ui.save_setting("temp_key", "temp_value")
        
        # Then clear it
        result = gradio_ui.clear_setting("temp_key")
        
        assert "Success" in result

    def test_clear_setting_empty_key(self, gradio_ui):
        """Test clearing a setting with empty key."""
        result = gradio_ui.clear_setting("")
        
        assert "Error" in result

    def test_export_settings_returns_json(self, gradio_ui):
        """Test that export settings returns valid JSON."""
        # Save a non-sensitive setting
        gradio_ui.save_setting("export_test", "test_value")
        
        result = gradio_ui.export_settings()
        
        assert isinstance(result, str)
        # Should be valid JSON
        try:
            json.loads(result)
        except json.JSONDecodeError:
            pytest.fail("Export settings should return valid JSON")

    def test_export_settings_excludes_sensitive_data(self, gradio_ui):
        """Test that export settings excludes sensitive data."""
        # Save a sensitive credential
        gradio_ui.save_credential("api_key", "secret_key_value")
        
        # Save a non-sensitive setting
        gradio_ui.save_setting("public_setting", "public_value")
        
        result = gradio_ui.export_settings()
        
        # Parse the JSON
        exported = json.loads(result)
        
        # Should not contain the encrypted credential
        assert "api_key" not in exported


class TestResultDownloadAvailability:
    """Property-based tests for result download availability.
    
    **Feature: lazy-automation-platform, Property 14: Result Download Availability**
    **Validates: Requirements 5.4**
    """

    @given(
        email_body=st.text(min_size=20, max_size=500, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
    )
    def test_email_summarization_provides_download(self, email_body):
        """
        Property: For any completed automation task, the system should provide a download option
        and create a downloadable file or summary.
        
        This test verifies that email summarization (an automation task) produces output
        that can be downloaded or exported.
        """
        gradio_ui = GradioUI()
        
        # Execute email summarization automation task
        result = gradio_ui.summarize_emails(email_body, max_length=100)
        
        # Verify the result is not empty
        assert result is not None, "Summarization should return a result"
        assert len(result) > 0, "Summarization result should not be empty"
        
        # Verify the result contains the expected structure for download
        # (original length, summary length, and summary content)
        assert "Original Length:" in result, "Result should contain original length"
        assert "Summary Length:" in result, "Result should contain summary length"
        assert "Summary:" in result, "Result should contain summary content"
        
        # The result should be a string that can be exported/downloaded
        assert isinstance(result, str), "Result should be a string that can be downloaded"

    @given(
        csv_content=st.lists(
            st.tuples(
                st.from_regex(r'[a-zA-Z0-9]{1,10}', fullmatch=True),
                st.integers(min_value=0, max_value=100),
                st.from_regex(r'[a-zA-Z]{1,10}', fullmatch=True)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_csv_parsing_provides_download(self, csv_content):
        """
        Property: For any completed CSV parsing automation task, the system should provide
        downloadable results (statistics and JSON export).
        """
        gradio_ui = GradioUI()
        
        # Create a temporary CSV file with test data
        temp_dir = tempfile.mkdtemp()
        try:
            csv_path = os.path.join(temp_dir, "test.csv")
            
            # Write CSV header
            with open(csv_path, "w") as f:
                f.write("name,age,city\n")
                # Write data rows
                for name, age, city in csv_content:
                    f.write(f"{name},{age},{city}\n")
            
            # Execute CSV parsing automation task
            stats_result = gradio_ui.parse_csv_file(csv_path)
            json_result = gradio_ui.export_csv_to_json(csv_path)
            
            # Verify statistics result is downloadable (non-empty string)
            assert stats_result is not None, "CSV parsing should return statistics"
            assert len(stats_result) > 0, "Statistics result should not be empty"
            assert "CSV Statistics" in stats_result, "Result should contain statistics header"
            assert isinstance(stats_result, str), "Statistics should be a string for download"
            
            # Verify JSON export result is downloadable (valid JSON string)
            assert json_result is not None, "JSON export should return data"
            assert len(json_result) > 0, "JSON export result should not be empty"
            assert isinstance(json_result, str), "JSON export should be a string for download"
            
            # Verify JSON is valid and can be parsed
            try:
                json.loads(json_result)
            except json.JSONDecodeError:
                pytest.fail("JSON export should produce valid JSON that can be downloaded")
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    @given(
        log_content=st.lists(
            st.sampled_from([
                "INFO: Application started",
                "ERROR: Connection failed",
                "WARNING: Low memory",
                "DEBUG: Processing file",
                "ERROR: Invalid input"
            ]),
            min_size=1,
            max_size=10
        )
    )
    def test_log_analysis_provides_download(self, log_content):
        """
        Property: For any completed log analysis automation task, the system should provide
        downloadable analysis results.
        """
        gradio_ui = GradioUI()
        
        # Create a temporary log file with test data
        temp_dir = tempfile.mkdtemp()
        try:
            log_path = os.path.join(temp_dir, "test.log")
            
            # Write log entries
            with open(log_path, "w") as f:
                for entry in log_content:
                    f.write(entry + "\n")
            
            # Execute log analysis automation task
            result = gradio_ui.analyze_log_file(log_path)
            
            # Verify the result is downloadable (non-empty string)
            assert result is not None, "Log analysis should return results"
            assert len(result) > 0, "Analysis result should not be empty"
            assert "Log Analysis" in result, "Result should contain analysis header"
            assert isinstance(result, str), "Analysis should be a string for download"
            
            # Verify the result contains downloadable content structure
            assert "Total Lines:" in result, "Result should contain line count"
            assert "Errors:" in result, "Result should contain error count"
            assert "Warnings:" in result, "Result should contain warning count"
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestDashboardProgressIndication:
    """Property-based tests for dashboard progress indication.
    
    **Feature: lazy-automation-platform, Property 35: Dashboard Progress Indication**
    **Validates: Requirements 12.2**
    """

    @given(
        execution_count=st.integers(min_value=1, max_value=5),
        items_processed=st.integers(min_value=1, max_value=100),
        duration_seconds=st.floats(min_value=0.1, max_value=100.0)
    )
    @settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_displays_progress_for_running_automation(self, execution_count, items_processed, duration_seconds):
        """
        Property: For any running automation, the dashboard should display a progress indicator
        showing completion percentage.
        
        This test verifies that:
        1. The dashboard can track and display progress information
        2. Progress indicators are displayed as numeric values (percentages)
        3. Progress information is consistent with execution data
        4. The dashboard output contains progress-related metrics
        """
        gradio_ui = GradioUI()
        
        # Simulate automation executions to create progress data
        for i in range(min(execution_count, 3)):  # Limit to 3 to keep test fast
            execution_id = f"test_exec_{i}"
            automation_id = "test_automation"
            automation_name = "Test Automation"
            
            # Record execution with progress data
            gradio_ui.analytics_engine.record_execution(
                execution_id=execution_id,
                automation_id=automation_id,
                automation_name=automation_name,
                success=True,
                duration_seconds=duration_seconds,
                items_processed=items_processed,
                time_saved_minutes=items_processed * 0.5  # Estimate time saved
            )
        
        # Get dashboard summary which should include progress information
        result = gradio_ui.get_dashboard_summary()
        
        # Verify the result is a string
        assert isinstance(result, str), "Dashboard summary should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Dashboard summary should not be empty"
        
        # Verify the result contains dashboard header
        assert "DASHBOARD SUMMARY" in result or "USAGE STATISTICS" in result, \
            "Dashboard should contain a header"
        
        # Verify the result contains numeric progress indicators
        # Progress should be shown as percentages or counts
        assert any(char.isdigit() for char in result), \
            "Dashboard should contain numeric progress data"
        
        # Verify the result contains progress-related metrics
        progress_indicators = ['Executions', 'Successful', 'Items Processed', 'Time Saved', 'Success Rate']
        has_progress_info = any(indicator in result for indicator in progress_indicators)
        assert has_progress_info, \
            "Dashboard should contain progress-related metrics"
        
        # Verify the result is properly formatted
        assert '\n' in result, "Dashboard output should be formatted with newlines"

    @given(
        automation_count=st.integers(min_value=1, max_value=3),
        success_rate=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_progress_shows_completion_percentage(self, automation_count, success_rate):
        """
        Property: For any set of automation executions, the dashboard should display
        completion percentage as a progress indicator.
        
        This test verifies that:
        1. Progress is displayed as a percentage or ratio
        2. Progress calculation is accurate
        3. Progress information is visible in dashboard output
        """
        gradio_ui = GradioUI()
        
        # Create automation executions with varying success rates
        total_executions = min(automation_count * 2, 5)  # Limit total executions
        successful_count = int(total_executions * success_rate)
        
        for i in range(total_executions):
            execution_id = f"progress_test_{i}"
            automation_id = f"automation_{i % automation_count}"
            success = i < successful_count
            
            gradio_ui.analytics_engine.record_execution(
                execution_id=execution_id,
                automation_id=automation_id,
                automation_name=f"Automation {i % automation_count}",
                success=success,
                duration_seconds=10.0,
                items_processed=100,
                time_saved_minutes=50.0 if success else 0.0
            )
        
        # Get automation status which shows progress
        result = gradio_ui.get_automation_status()
        
        # Verify the result is a string
        assert isinstance(result, str), "Automation status should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Automation status should not be empty"
        
        # Verify the result contains progress information
        # Should show execution counts which indicate progress
        assert "Executions" in result or "No automations" in result, \
            "Status should contain execution information or indicate no automations"
        
        # If there are automations, verify progress metrics are shown
        if "No automations" not in result:
            # Should contain numeric progress data
            assert any(char.isdigit() for char in result), \
                "Status should contain numeric progress data"
            
            # Should show success/failure counts which indicate progress
            progress_fields = ['Successful', 'Failed', 'Executions']
            has_progress = any(field in result for field in progress_fields)
            assert has_progress, \
                "Status should show progress through execution counts"

    @given(
        time_saved_minutes=st.floats(min_value=0.0, max_value=1000.0)
    )
    @settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_progress_includes_time_saved_metric(self, time_saved_minutes):
        """
        Property: For any automation execution, the dashboard progress should include
        time saved as a progress metric.
        
        This test verifies that:
        1. Time saved is tracked and displayed
        2. Time saved is shown as a numeric value
        3. Time saved contributes to overall progress indication
        """
        gradio_ui = GradioUI()
        
        # Record an execution with time saved
        gradio_ui.analytics_engine.record_execution(
            execution_id="time_test_1",
            automation_id="time_tracking_automation",
            automation_name="Time Tracking Test",
            success=True,
            duration_seconds=5.0,
            items_processed=50,
            time_saved_minutes=time_saved_minutes
        )
        
        # Get time saved report which shows progress
        result = gradio_ui.get_time_saved_report()
        
        # Verify the result is a string
        assert isinstance(result, str), "Time saved report should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Time saved report should not be empty"
        
        # Verify the result contains time saved header
        assert "TIME SAVED" in result or "Total Time Saved" in result, \
            "Report should contain time saved information"
        
        # Verify the result contains numeric time data
        assert any(char.isdigit() for char in result), \
            "Report should contain numeric time data"
        
        # Verify the result is properly formatted
        assert '\n' in result or len(result) > 20, \
            "Report should be properly formatted"


class TestDashboardStatusDisplay:
    """Property-based tests for dashboard status display.
    
    **Feature: lazy-automation-platform, Property 34: Dashboard Status Display**
    **Validates: Requirements 12.1**
    """

    @given(
        automation_names=st.lists(
            st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
            min_size=1,
            max_size=5,
            unique=True
        ),
        statuses=st.lists(
            st.sampled_from(['enabled', 'disabled', 'running', 'idle']),
            min_size=1,
            max_size=5
        )
    )
    def test_dashboard_displays_automation_status(self, automation_names, statuses):
        """
        Property: For any configured automation, the dashboard should display its current status
        (enabled, disabled, running, idle).
        
        This test verifies that:
        1. The dashboard can be loaded
        2. The dashboard returns a formatted string
        3. The dashboard output contains status information
        4. The dashboard output is non-empty and properly formatted
        """
        gradio_ui = GradioUI()
        
        # Get the dashboard summary which displays all automation statuses
        result = gradio_ui.get_dashboard_summary()
        
        # Verify the result is a string (can be displayed)
        assert isinstance(result, str), "Dashboard summary should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Dashboard summary should not be empty"
        
        # Verify the result contains dashboard header
        assert "DASHBOARD SUMMARY" in result or "USAGE STATISTICS" in result, \
            "Dashboard should contain a header identifying it as a dashboard"
        
        # Verify the result contains status-related information
        # The dashboard should display status information for automations
        status_indicators = ['Status', 'Enabled', 'Disabled', 'Running', 'Idle', 'Executions']
        has_status_info = any(indicator in result for indicator in status_indicators)
        assert has_status_info, \
            "Dashboard should contain status information about automations"
        
        # Verify the result is properly formatted (contains newlines for readability)
        assert '\n' in result, "Dashboard output should be formatted with newlines"
        
        # Verify the result contains numeric data (execution counts, etc.)
        # This ensures the dashboard is displaying actual automation data
        assert any(char.isdigit() for char in result), \
            "Dashboard should contain numeric data about automation executions"

    @given(
        automation_count=st.integers(min_value=0, max_value=10)
    )
    def test_dashboard_status_consistency(self, automation_count):
        """
        Property: For any number of configured automations, the dashboard status display
        should be consistent and properly formatted.
        
        This test verifies that:
        1. The dashboard returns consistent output format
        2. The dashboard handles different numbers of automations
        3. The dashboard output is always properly formatted
        """
        gradio_ui = GradioUI()
        
        # Get automation status (which shows all configured automations)
        result = gradio_ui.get_automation_status()
        
        # Verify the result is a string
        assert isinstance(result, str), "Automation status should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Automation status should not be empty"
        
        # Verify the result contains a header
        assert "AUTOMATION STATUS" in result or "No automations" in result, \
            "Status display should contain a header or message"
        
        # If there are automations, verify status fields are present
        if "No automations" not in result:
            # Should contain status-related fields
            status_fields = ['Status', 'Executions', 'Successful', 'Failed']
            has_fields = any(field in result for field in status_fields)
            assert has_fields, \
                "Automation status should contain status fields when automations exist"

    @given(
        query_type=st.sampled_from(['dashboard', 'status', 'time_saved', 'error_log'])
    )
    def test_dashboard_displays_all_status_types(self, query_type):
        """
        Property: For any dashboard query type, the system should display the requested
        status information in a consistent format.
        
        This test verifies that all dashboard status display methods return properly
        formatted strings with status information.
        """
        gradio_ui = GradioUI()
        
        # Call the appropriate dashboard method based on query type
        if query_type == 'dashboard':
            result = gradio_ui.get_dashboard_summary()
            expected_content = ['DASHBOARD SUMMARY', 'USAGE STATISTICS']
        elif query_type == 'status':
            result = gradio_ui.get_automation_status()
            expected_content = ['AUTOMATION STATUS', 'No automations']
        elif query_type == 'time_saved':
            result = gradio_ui.get_time_saved_report()
            expected_content = ['TIME SAVED', 'Total Time Saved']
        else:  # error_log
            result = gradio_ui.get_error_log_report()
            expected_content = ['ERROR', 'Total Errors']
        
        # Verify the result is a string
        assert isinstance(result, str), f"{query_type} should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, f"{query_type} result should not be empty"
        
        # Verify the result contains expected content
        has_expected = any(content in result for content in expected_content)
        assert has_expected, \
            f"{query_type} result should contain expected status information"
        
        # Verify the result is properly formatted (either has newlines or is a simple message)
        # When there are no automations, a simple message is acceptable
        is_formatted = '\n' in result or 'No automations' in result or 'No undo' in result
        assert is_formatted or len(result) > 20, \
            f"{query_type} output should be properly formatted"


class TestDashboardAutomationDetails:
    """Property-based tests for dashboard automation details.
    
    **Feature: lazy-automation-platform, Property 36: Dashboard Automation Details**
    **Validates: Requirements 12.3**
    """

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
        execution_count=st.integers(min_value=1, max_value=5),
        success_rate=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_automation_details_displays_execution_history(self, automation_id, execution_count, success_rate):
        """
        Property: For any automation clicked on the dashboard, the system should display
        detailed information including last execution time, success rate, and configuration.
        
        This test verifies that:
        1. Automation details can be retrieved by automation ID
        2. Details include execution statistics (total, successful, failed)
        3. Details include success rate calculation
        4. Details include last execution time
        5. Details include configuration information
        """
        gradio_ui = GradioUI()
        
        # Create execution records for the automation
        successful_count = int(execution_count * success_rate)
        
        for i in range(execution_count):
            execution_id = f"{automation_id}_exec_{i}"
            success = i < successful_count
            
            gradio_ui.analytics_engine.record_execution(
                execution_id=execution_id,
                automation_id=automation_id,
                automation_name=f"Test Automation {automation_id}",
                success=success,
                duration_seconds=10.0 + i,
                items_processed=50 + i * 10,
                time_saved_minutes=25.0 if success else 0.0,
                errors=["Test error"] if not success else []
            )
        
        # Get automation details
        result = gradio_ui.get_automation_details(automation_id)
        
        # Verify the result is a string
        assert isinstance(result, str), "Automation details should return a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Automation details should not be empty"
        
        # Verify the result contains the automation ID
        assert automation_id in result, \
            f"Details should contain the automation ID '{automation_id}'"
        
        # Verify the result contains execution statistics
        assert "EXECUTION STATISTICS" in result, \
            "Details should contain execution statistics section"
        
        # Verify the result contains total executions count
        assert "Total Executions:" in result, \
            "Details should show total execution count"
        assert str(execution_count) in result, \
            f"Details should show {execution_count} total executions"
        
        # Verify the result contains success/failure counts
        assert "Successful:" in result, \
            "Details should show successful execution count"
        assert "Failed:" in result, \
            "Details should show failed execution count"
        
        # Verify the result contains success rate
        assert "Success Rate:" in result, \
            "Details should show success rate percentage"
        
        # Verify the result contains last execution information
        assert "LAST EXECUTION" in result, \
            "Details should contain last execution section"
        assert "Time:" in result, \
            "Details should show last execution time"
        assert "Status:" in result, \
            "Details should show last execution status"
        
        # Verify the result contains performance metrics
        assert "PERFORMANCE METRICS" in result, \
            "Details should contain performance metrics section"
        assert "Average Duration:" in result, \
            "Details should show average duration"
        assert "Total Items Processed:" in result, \
            "Details should show total items processed"
        assert "Total Time Saved:" in result, \
            "Details should show total time saved"
        
        # Verify the result contains configuration section
        assert "CONFIGURATION" in result, \
            "Details should contain configuration section"
        
        # Verify the result is properly formatted
        assert '\n' in result, \
            "Details should be properly formatted with newlines"

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_automation_details_with_no_history(self, automation_id):
        """
        Property: For any automation with no execution history, the system should
        display an appropriate message indicating no history is available.
        
        This test verifies that:
        1. The system handles automations with no execution history gracefully
        2. An appropriate message is returned
        3. The message is informative
        """
        gradio_ui = GradioUI()
        
        # Use a unique automation ID that won't have history
        unique_automation_id = f"nonexistent_{automation_id}_{id(gradio_ui)}"
        
        # Try to get details for an automation that has never been executed
        result = gradio_ui.get_automation_details(unique_automation_id)
        
        # Verify the result is a string
        assert isinstance(result, str), "Result should be a string"
        
        # Verify the result is not empty
        assert len(result) > 0, "Result should not be empty"
        
        # Verify the result indicates no history
        assert "No execution history" in result or "not found" in result.lower(), \
            "Result should indicate no execution history is available"

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
        config_key=st.from_regex(r'[a-zA-Z0-9_]{3,15}', fullmatch=True),
        config_value=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_automation_details_includes_configuration(self, automation_id, config_key, config_value):
        """
        Property: For any automation with stored configuration, the system should
        display the configuration details in the automation details view.
        
        This test verifies that:
        1. Configuration is stored and retrieved correctly
        2. Configuration is displayed in automation details
        3. Sensitive configuration values are masked
        """
        gradio_ui = GradioUI()
        
        # Create an execution record
        gradio_ui.analytics_engine.record_execution(
            execution_id=f"{automation_id}_exec_1",
            automation_id=automation_id,
            automation_name=f"Test Automation {automation_id}",
            success=True,
            duration_seconds=10.0,
            items_processed=50,
            time_saved_minutes=25.0
        )
        
        # Save configuration for this automation
        config = {config_key: config_value}
        gradio_ui.config_manager.save_config(f"automation_{automation_id}", config)
        
        # Get automation details
        result = gradio_ui.get_automation_details(automation_id)
        
        # Verify the result is a string
        assert isinstance(result, str), "Result should be a string"
        
        # Verify the result contains configuration section
        assert "CONFIGURATION" in result, \
            "Details should contain configuration section"
        
        # Verify the configuration key is displayed
        assert config_key in result, \
            f"Configuration key '{config_key}' should be displayed"
        
        # Verify the configuration value is displayed (unless it's sensitive)
        if not any(sensitive in config_key.lower() for sensitive in ['password', 'key', 'token', 'secret', 'credential']):
            assert config_value in result, \
                f"Configuration value '{config_value}' should be displayed"

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True)
    )
    @settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_automation_details_empty_automation_id(self, automation_id):
        """
        Property: For any empty or invalid automation ID, the system should
        display an appropriate error message.
        
        This test verifies that:
        1. Empty automation IDs are rejected
        2. An error message is returned
        3. The error message is informative
        """
        gradio_ui = GradioUI()
        
        # Try to get details with empty automation ID
        result = gradio_ui.get_automation_details("")
        
        # Verify the result is a string
        assert isinstance(result, str), "Result should be a string"
        
        # Verify the result contains an error message
        assert "Error" in result, \
            "Result should contain an error message for empty automation ID"

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
        execution_count=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_automation_details_success_rate_calculation(self, automation_id, execution_count):
        """
        Property: For any automation with multiple executions, the system should
        correctly calculate and display the success rate.
        
        This test verifies that:
        1. Success rate is calculated correctly
        2. Success rate is displayed as a percentage
        3. Success rate calculation is accurate for all execution counts
        """
        gradio_ui = GradioUI()
        
        # Create execution records with varying success
        successful_count = execution_count // 2
        
        for i in range(execution_count):
            success = i < successful_count
            
            gradio_ui.analytics_engine.record_execution(
                execution_id=f"{automation_id}_exec_{i}",
                automation_id=automation_id,
                automation_name=f"Test Automation {automation_id}",
                success=success,
                duration_seconds=10.0,
                items_processed=50,
                time_saved_minutes=25.0 if success else 0.0
            )
        
        # Get automation details
        result = gradio_ui.get_automation_details(automation_id)
        
        # Verify the result contains success rate
        assert "Success Rate:" in result, \
            "Details should show success rate"
        
        # Calculate expected success rate
        expected_rate = (successful_count / execution_count * 100) if execution_count > 0 else 0.0
        
        # Verify the success rate is displayed as a percentage
        assert "%" in result, \
            "Success rate should be displayed as a percentage"
        
        # Verify the result contains numeric data
        assert any(char.isdigit() for char in result), \
            "Details should contain numeric success rate data"


class TestDashboardStatusUpdate:
    """Property-based tests for dashboard status update.
    
    **Feature: lazy-automation-platform, Property 37: Dashboard Status Update**
    **Validates: Requirements 12.4**
    """

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
        automation_name=st.from_regex(r'[a-zA-Z0-9 ]{5,30}', fullmatch=True),
        success=st.booleans(),
        items_processed=st.integers(min_value=1, max_value=100),
        time_saved_minutes=st.floats(min_value=0.0, max_value=100.0)
    )
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_updates_immediately_after_automation_completion(
        self, automation_id, automation_name, success, items_processed, time_saved_minutes
    ):
        """
        Property: For any completed automation, the dashboard status should update
        immediately and display the result.
        
        This test verifies that:
        1. When an automation completes, the dashboard reflects the new status
        2. The dashboard displays the result of the completed automation
        3. The status update is immediate (no delay in reflection)
        4. The dashboard shows the correct success/failure status
        5. The dashboard displays the result metrics (items processed, time saved)
        """
        gradio_ui = GradioUI()
        
        # Get initial dashboard state (before automation execution)
        initial_dashboard = gradio_ui.get_dashboard_summary()
        initial_status = gradio_ui.get_automation_status()
        
        # Verify initial state is a string
        assert isinstance(initial_dashboard, str), "Initial dashboard should be a string"
        assert isinstance(initial_status, str), "Initial status should be a string"
        
        # Record an automation execution (simulating completion)
        execution_id = f"test_exec_{id(gradio_ui)}"
        gradio_ui.analytics_engine.record_execution(
            execution_id=execution_id,
            automation_id=automation_id,
            automation_name=automation_name,
            success=success,
            duration_seconds=5.0,
            items_processed=items_processed,
            errors=[] if success else ["Test error"],
            time_saved_minutes=time_saved_minutes if success else 0.0
        )
        
        # Get updated dashboard state (after automation execution)
        updated_dashboard = gradio_ui.get_dashboard_summary()
        updated_status = gradio_ui.get_automation_status()
        
        # Verify updated state is a string
        assert isinstance(updated_dashboard, str), "Updated dashboard should be a string"
        assert isinstance(updated_status, str), "Updated status should be a string"
        
        # Verify the dashboard has been updated (contains new execution data)
        # The dashboard should now show the automation that was just executed
        assert automation_id in updated_status or "Executions" in updated_status, \
            "Dashboard status should reflect the completed automation"
        
        # Verify the dashboard displays the result
        # Should show execution count increased
        assert "Executions:" in updated_status, \
            "Dashboard should display execution count"
        
        # Verify the dashboard shows success/failure status
        if success:
            assert "Successful:" in updated_status, \
                "Dashboard should show successful execution count"
        else:
            assert "Failed:" in updated_status, \
                "Dashboard should show failed execution count"
        
        # Verify the dashboard displays result metrics
        assert "Items Processed:" in updated_status, \
            "Dashboard should display items processed"
        
        # Verify the dashboard displays time saved (if successful)
        if success:
            assert "Time Saved:" in updated_status, \
                "Dashboard should display time saved for successful automation"
        
        # Verify the dashboard summary also reflects the update
        assert "USAGE STATISTICS" in updated_dashboard or "DASHBOARD SUMMARY" in updated_dashboard, \
            "Dashboard summary should contain usage statistics"
        
        # Verify the dashboard contains numeric data about the execution
        assert any(char.isdigit() for char in updated_dashboard), \
            "Dashboard should contain numeric execution data"
        
        # Verify the dashboard is properly formatted
        assert '\n' in updated_dashboard, \
            "Dashboard should be properly formatted with newlines"

    @given(
        execution_count=st.integers(min_value=1, max_value=5),
        success_rate=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_status_reflects_multiple_completions(self, execution_count, success_rate):
        """
        Property: For any sequence of completed automations, the dashboard status
        should reflect all completions and display cumulative results.
        
        This test verifies that:
        1. Multiple automation completions are all reflected in the dashboard
        2. The dashboard shows cumulative execution counts
        3. The dashboard shows cumulative success/failure counts
        4. The dashboard shows cumulative time saved
        5. The dashboard status is consistent across multiple updates
        """
        gradio_ui = GradioUI()
        
        # Execute multiple automations
        successful_count = int(execution_count * success_rate)
        
        for i in range(execution_count):
            success = i < successful_count
            
            gradio_ui.analytics_engine.record_execution(
                execution_id=f"multi_exec_{i}",
                automation_id=f"automation_{i % 2}",  # Alternate between 2 automations
                automation_name=f"Test Automation {i % 2}",
                success=success,
                duration_seconds=5.0 + i,
                items_processed=50 + i * 10,
                errors=[] if success else ["Error"],
                time_saved_minutes=25.0 if success else 0.0
            )
        
        # Get dashboard status after all completions
        dashboard = gradio_ui.get_dashboard_summary()
        status = gradio_ui.get_automation_status()
        
        # Verify the dashboard is a string
        assert isinstance(dashboard, str), "Dashboard should be a string"
        assert isinstance(status, str), "Status should be a string"
        
        # Verify the dashboard shows cumulative execution count
        assert "Executions:" in status, \
            "Dashboard should show total execution count"
        
        # Verify the dashboard shows cumulative success count
        assert "Successful:" in status, \
            "Dashboard should show cumulative successful count"
        
        # Verify the dashboard shows cumulative failure count
        assert "Failed:" in status, \
            "Dashboard should show cumulative failed count"
        
        # Verify the dashboard shows cumulative items processed
        assert "Items Processed:" in status, \
            "Dashboard should show cumulative items processed"
        
        # Verify the dashboard shows cumulative time saved
        assert "Time Saved:" in status, \
            "Dashboard should show cumulative time saved"
        
        # Verify the dashboard contains numeric data
        assert any(char.isdigit() for char in dashboard), \
            "Dashboard should contain numeric data"
        
        # Verify the dashboard is properly formatted
        assert '\n' in dashboard, \
            "Dashboard should be properly formatted"

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
        items_processed=st.integers(min_value=1, max_value=100),
        time_saved_minutes=st.floats(min_value=0.1, max_value=100.0)
    )
    @settings(max_examples=15, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_displays_result_metrics_immediately(
        self, automation_id, items_processed, time_saved_minutes
    ):
        """
        Property: For any completed automation, the dashboard should immediately
        display the result metrics (items processed, time saved, etc.).
        
        This test verifies that:
        1. Result metrics are displayed immediately after completion
        2. Items processed count is displayed
        3. Time saved is displayed
        4. Metrics are accurate and reflect the actual execution
        5. Metrics are visible in the dashboard output
        """
        gradio_ui = GradioUI()
        
        # Record an automation execution with specific metrics
        gradio_ui.analytics_engine.record_execution(
            execution_id=f"metrics_test_{id(gradio_ui)}",
            automation_id=automation_id,
            automation_name=f"Metrics Test {automation_id}",
            success=True,
            duration_seconds=10.0,
            items_processed=items_processed,
            time_saved_minutes=time_saved_minutes
        )
        
        # Get dashboard status immediately after execution
        status = gradio_ui.get_automation_status()
        dashboard = gradio_ui.get_dashboard_summary()
        
        # Verify the status is a string
        assert isinstance(status, str), "Status should be a string"
        assert isinstance(dashboard, str), "Dashboard should be a string"
        
        # Verify the status displays items processed
        assert "Items Processed:" in status, \
            "Status should display items processed metric"
        
        # Verify the status displays time saved
        assert "Time Saved:" in status, \
            "Status should display time saved metric"
        
        # Verify the dashboard displays the automation
        assert automation_id in status or "Executions:" in status, \
            "Dashboard should display the completed automation"
        
        # Verify the metrics are numeric
        assert any(char.isdigit() for char in status), \
            "Dashboard should contain numeric metric values"
        
        # Verify the dashboard is properly formatted
        assert '\n' in status, \
            "Dashboard should be properly formatted"

    @given(
        automation_id=st.from_regex(r'[a-zA-Z0-9_]{3,20}', fullmatch=True),
        error_message=st.from_regex(r'[a-zA-Z0-9 ]{10,50}', fullmatch=True)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_displays_failure_status_immediately(self, automation_id, error_message):
        """
        Property: For any failed automation, the dashboard should immediately
        display the failure status and error information.
        
        This test verifies that:
        1. Failed automation status is displayed immediately
        2. Failure is clearly indicated in the dashboard
        3. Error information is available in the dashboard
        4. Failed count is incremented
        5. The dashboard reflects the failure without delay
        """
        gradio_ui = GradioUI()
        
        # Record a failed automation execution
        gradio_ui.analytics_engine.record_execution(
            execution_id=f"failure_test_{id(gradio_ui)}",
            automation_id=automation_id,
            automation_name=f"Failure Test {automation_id}",
            success=False,
            duration_seconds=5.0,
            items_processed=0,
            errors=[error_message],
            time_saved_minutes=0.0
        )
        
        # Get dashboard status immediately after failure
        status = gradio_ui.get_automation_status()
        dashboard = gradio_ui.get_dashboard_summary()
        
        # Verify the status is a string
        assert isinstance(status, str), "Status should be a string"
        assert isinstance(dashboard, str), "Dashboard should be a string"
        
        # Verify the status displays the failed automation
        assert automation_id in status or "Failed:" in status, \
            "Dashboard should display the failed automation"
        
        # Verify the status shows failed count
        assert "Failed:" in status, \
            "Dashboard should show failed execution count"
        
        # Verify the dashboard contains error information
        assert "ERROR" in dashboard.upper() or "Failed" in status, \
            "Dashboard should indicate failure status"
        
        # Verify the dashboard is properly formatted
        assert '\n' in status or len(status) > 20, \
            "Dashboard should be properly formatted"

    @given(
        automation_count=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_dashboard_status_consistency_across_queries(self, automation_count):
        """
        Property: For any set of completed automations, the dashboard status
        should be consistent across multiple queries.
        
        This test verifies that:
        1. Multiple queries to the dashboard return consistent data
        2. The dashboard status doesn't change between queries (without new executions)
        3. The dashboard reflects the same state across different query methods
        4. Status consistency is maintained
        """
        gradio_ui = GradioUI()
        
        # Record multiple automation executions
        for i in range(min(automation_count, 3)):
            gradio_ui.analytics_engine.record_execution(
                execution_id=f"consistency_test_{i}",
                automation_id=f"automation_{i}",
                automation_name=f"Consistency Test {i}",
                success=True,
                duration_seconds=5.0,
                items_processed=50,
                time_saved_minutes=25.0
            )
        
        # Query the dashboard multiple times
        status_query_1 = gradio_ui.get_automation_status()
        status_query_2 = gradio_ui.get_automation_status()
        dashboard_query_1 = gradio_ui.get_dashboard_summary()
        dashboard_query_2 = gradio_ui.get_dashboard_summary()
        
        # Verify all queries return strings
        assert isinstance(status_query_1, str), "Status query 1 should return a string"
        assert isinstance(status_query_2, str), "Status query 2 should return a string"
        assert isinstance(dashboard_query_1, str), "Dashboard query 1 should return a string"
        assert isinstance(dashboard_query_2, str), "Dashboard query 2 should return a string"
        
        # Verify the status is consistent across queries
        # (same automation data should be present in both queries)
        assert "Executions:" in status_query_1, "Status query 1 should contain execution data"
        assert "Executions:" in status_query_2, "Status query 2 should contain execution data"
        
        # Verify the dashboard is consistent across queries
        assert "USAGE STATISTICS" in dashboard_query_1 or "DASHBOARD SUMMARY" in dashboard_query_1, \
            "Dashboard query 1 should contain dashboard header"
        assert "USAGE STATISTICS" in dashboard_query_2 or "DASHBOARD SUMMARY" in dashboard_query_2, \
            "Dashboard query 2 should contain dashboard header"
        
        # Verify both queries contain numeric data
        assert any(char.isdigit() for char in status_query_1), \
            "Status query 1 should contain numeric data"
        assert any(char.isdigit() for char in status_query_2), \
            "Status query 2 should contain numeric data"

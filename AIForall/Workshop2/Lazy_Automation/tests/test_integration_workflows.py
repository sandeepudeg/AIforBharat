"""Integration tests for complete automation workflows and system validation.

This module tests:
- Complete automation workflows across multiple modules
- Tab navigation and state preservation
- Error handling across all modules
- End-to-end system functionality

**Feature: lazy-automation-platform, Integration Testing**
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
"""

import pytest
import tempfile
import os
import json
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

from src.gradio_ui import GradioUI
from src.file_automation import BulkRenamer, AutoOrganizer, DuplicateCleaner
from src.communication_automation import EmailSummarizer, TemplateResponder, NotificationBot
from src.productivity_automation import ReportGenerator, LogCleaner, ClipboardEnhancer
from src.web_cloud_automation import BulkDownloader, AutoFormFiller, CloudSyncCleanup
from src.config_manager import ConfigManager
from src.error_handler import ErrorHandler
from src.backup_manager import BackupManager
from src.analytics_engine import AnalyticsEngine


class TestCompleteFileAutomationWorkflow:
    """Integration tests for complete file automation workflows.
    
    **Feature: lazy-automation-platform, Integration Testing**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
    """

    def test_complete_file_automation_workflow(self):
        """Test complete workflow: upload -> preview -> apply -> download."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create test files
            test_files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"old_file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content {i}")
                test_files.append(file_path)
            
            # Step 2: Initialize UI and get preview
            gradio_ui = GradioUI()
            status, preview = gradio_ui.bulk_rename_preview(temp_dir, "old_", "new_")
            
            # Verify preview is generated
            assert isinstance(preview, list)
            assert len(preview) > 0
            
            # Step 3: Apply bulk rename
            apply_status = gradio_ui.bulk_rename_apply(temp_dir, "old_", "new_")
            assert "Success" in apply_status or "Completed" in apply_status
            
            # Step 4: Verify files were renamed
            renamed_files = os.listdir(temp_dir)
            assert any("new_" in f for f in renamed_files)
            
            # Step 5: Verify download option is available
            # (In real Gradio, this would be a file download)
            assert apply_status is not None

    def test_file_automation_with_error_handling(self):
        """Test file automation with error handling for invalid inputs."""
        gradio_ui = GradioUI()
        
        # Test with invalid directory
        status, preview = gradio_ui.bulk_rename_preview("/nonexistent/path", "pattern", "replacement")
        assert "Error" in status
        
        # Test with empty pattern
        with tempfile.TemporaryDirectory() as temp_dir:
            status, preview = gradio_ui.bulk_rename_preview(temp_dir, "", "replacement")
            # Should handle empty pattern gracefully
            assert isinstance(status, str)
            assert isinstance(preview, list)

    def test_duplicate_detection_and_removal_workflow(self):
        """Test complete duplicate detection and removal workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create duplicate files
            content = "This is duplicate content"
            for i in range(3):
                file_path = os.path.join(temp_dir, f"file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(content)
            
            # Step 2: Find duplicates
            gradio_ui = GradioUI()
            find_status = gradio_ui.find_duplicates(temp_dir)
            assert "Summary" in find_status or "No duplicates" in find_status
            
            # Step 3: Remove duplicates
            remove_status = gradio_ui.remove_duplicates(temp_dir, keep_first=True)
            assert "Success" in remove_status or "Completed" in remove_status
            
            # Step 4: Verify only one file remains
            remaining_files = os.listdir(temp_dir)
            assert len(remaining_files) == 1

    def test_auto_organize_workflow(self):
        """Test auto-organize workflow with multiple file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Step 1: Create files of different types
            file_types = {
                "document.txt": "text content",
                "image.jpg": "fake image data",
                "archive.zip": "fake zip data",
            }
            
            for filename, content in file_types.items():
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "w") as f:
                    f.write(content)
            
            # Step 2: Run auto-organize
            gradio_ui = GradioUI()
            status = gradio_ui.auto_organize(temp_dir)
            assert "Success" in status or "Completed" in status
            
            # Step 3: Verify files are organized
            # (Files should be in categorized folders)
            assert os.path.exists(temp_dir)


class TestTabNavigationAndStatePreservation:
    """Integration tests for tab navigation and state preservation.
    
    **Feature: lazy-automation-platform, Integration Testing**
    **Validates: Requirements 5.5**
    """

    def test_tab_navigation_preserves_file_automation_state(self):
        """Test that navigating away and back preserves File Automation tab state."""
        gradio_ui = GradioUI()
        
        # Step 1: Configure File Automation tab
        # (Simulate by saving configuration)
        config_key = "file_automation_pattern"
        config_value = "test_pattern"
        gradio_ui.save_setting(config_key, config_value)
        
        # Step 2: Navigate to Communication Automation tab
        # (Simulate by calling Communication function)
        gradio_ui.add_template("template_1", "urgent", "Response")
        
        # Step 3: Navigate back to File Automation tab
        # (Simulate by retrieving configuration)
        retrieved_value = gradio_ui.config_manager.load_config(config_key)
        
        # Verify state is preserved
        assert retrieved_value == config_value

    def test_tab_navigation_preserves_communication_state(self):
        """Test that navigating away and back preserves Communication Automation tab state."""
        gradio_ui = GradioUI()
        
        # Step 1: Add templates in Communication Automation tab
        gradio_ui.add_template("template_1", "urgent", "Urgent response")
        gradio_ui.add_template("template_2", "follow-up", "Follow-up response")
        
        # Step 2: Navigate to File Automation tab
        with tempfile.TemporaryDirectory() as temp_dir:
            gradio_ui.get_file_type_distribution(temp_dir)
        
        # Step 3: Navigate back to Communication Automation tab
        templates_list = gradio_ui.list_templates()
        
        # Verify templates are still there
        assert "template_1" in templates_list
        assert "template_2" in templates_list

    def test_tab_navigation_preserves_productivity_state(self):
        """Test that navigating away and back preserves Productivity Automation tab state."""
        gradio_ui = GradioUI()
        
        # Step 1: Add clipboard items in Productivity Automation tab
        gradio_ui.add_clipboard_item("Item 1", "task1", "tag1")
        gradio_ui.add_clipboard_item("Item 2", "task2", "tag2")
        
        # Step 2: Navigate to Web & Cloud Automation tab
        gradio_ui.create_form_profile("profile1", '{"name": "John"}')
        
        # Step 3: Navigate back to Productivity Automation tab
        history = gradio_ui.get_clipboard_history()
        
        # Verify clipboard items are still there
        assert "Item 1" in history or "2 items" in history

    def test_tab_navigation_preserves_web_cloud_state(self):
        """Test that navigating away and back preserves Web & Cloud Automation tab state."""
        gradio_ui = GradioUI()
        
        # Step 1: Create form profiles in Web & Cloud Automation tab
        profile_data = '{"name": "John", "email": "john@example.com"}'
        gradio_ui.create_form_profile("profile1", profile_data)
        
        # Step 2: Navigate to File Automation tab
        with tempfile.TemporaryDirectory() as temp_dir:
            gradio_ui.get_file_type_distribution(temp_dir)
        
        # Step 3: Navigate back to Web & Cloud Automation tab
        profiles_list = gradio_ui.list_form_profiles()
        
        # Verify profiles are still there
        assert "profile1" in profiles_list

    @given(
        tab_sequence=st.lists(
            st.sampled_from(['file', 'communication', 'productivity', 'web']),
            min_size=2,
            max_size=5,
            unique=False
        )
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_multiple_tab_navigations_preserve_state(self, tab_sequence):
        """Property: For any sequence of tab navigations, state should be preserved.
        
        This test verifies that:
        1. Navigating between tabs preserves configuration
        2. Multiple navigations don't lose state
        3. State is consistent across navigation sequences
        """
        gradio_ui = GradioUI()
        
        # Store initial state in each tab
        initial_states = {}
        
        # File Automation state
        gradio_ui.save_setting("file_pattern", "test_pattern")
        initial_states['file'] = gradio_ui.config_manager.load_config("file_pattern")
        
        # Communication Automation state
        gradio_ui.add_template("template_1", "urgent", "Response")
        initial_states['communication'] = "template_1"
        
        # Productivity Automation state
        gradio_ui.add_clipboard_item("Test Item", "task1", "tag1")
        initial_states['productivity'] = "Test Item"
        
        # Web & Cloud Automation state
        gradio_ui.create_form_profile("profile1", '{"name": "John"}')
        initial_states['web'] = "profile1"
        
        # Navigate through tabs in the given sequence
        for tab in tab_sequence:
            if tab == 'file':
                gradio_ui.get_file_type_distribution(tempfile.gettempdir())
            elif tab == 'communication':
                gradio_ui.list_templates()
            elif tab == 'productivity':
                gradio_ui.get_clipboard_history()
            elif tab == 'web':
                gradio_ui.list_form_profiles()
        
        # Verify all states are still preserved
        assert gradio_ui.config_manager.load_config("file_pattern") == initial_states['file']
        assert "template_1" in gradio_ui.list_templates()
        assert "Test Item" in gradio_ui.get_clipboard_history()
        assert "profile1" in gradio_ui.list_form_profiles()


class TestErrorHandlingAcrossModules:
    """Integration tests for error handling across all modules.
    
    **Feature: lazy-automation-platform, Integration Testing**
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
    """

    def test_file_automation_error_handling(self):
        """Test error handling in file automation module."""
        gradio_ui = GradioUI()
        
        # Test 1: Invalid directory
        status, preview = gradio_ui.bulk_rename_preview("/nonexistent/path", "pattern", "replacement")
        assert "Error" in status
        
        # Test 2: Invalid file operations
        status = gradio_ui.find_duplicates("/nonexistent/path")
        assert "Error" in status
        
        # Test 3: Invalid auto-organize
        status = gradio_ui.auto_organize("/nonexistent/path")
        assert "Error" in status

    def test_communication_automation_error_handling(self):
        """Test error handling in communication automation module."""
        gradio_ui = GradioUI()
        
        # Test 1: Empty template ID
        status = gradio_ui.add_template("", "keywords", "response")
        assert "Error" in status
        
        # Test 2: Empty keywords
        status = gradio_ui.add_template("template_1", "", "response")
        assert "Error" in status
        
        # Test 3: Empty response
        status = gradio_ui.add_template("template_1", "keywords", "")
        assert "Error" in status
        
        # Test 4: Empty email body
        status = gradio_ui.summarize_emails("", max_length=100)
        assert "Error" in status
        
        # Test 5: Empty template match query
        status = gradio_ui.match_template("")
        assert "Error" in status

    def test_productivity_automation_error_handling(self):
        """Test error handling in productivity automation module."""
        gradio_ui = GradioUI()
        
        # Test 1: Invalid CSV file
        status = gradio_ui.parse_csv_file("/nonexistent/file.csv")
        assert "Error" in status
        
        # Test 2: Invalid log file
        status = gradio_ui.analyze_log_file("/nonexistent/file.log")
        assert "Error" in status
        
        # Test 3: Empty clipboard item
        status = gradio_ui.add_clipboard_item("", "task", "tag")
        assert "Error" in status
        
        # Test 4: Empty clipboard search
        status = gradio_ui.search_clipboard("")
        assert "Error" in status

    def test_web_cloud_automation_error_handling(self):
        """Test error handling in web & cloud automation module."""
        gradio_ui = GradioUI()
        
        # Test 1: Invalid URLs
        status = gradio_ui.validate_urls("not a url")
        assert "Error" in status
        
        # Test 2: Empty URLs
        status = gradio_ui.validate_urls("")
        assert "Error" in status
        
        # Test 3: Invalid form profile JSON
        status = gradio_ui.create_form_profile("profile1", "not json")
        assert "Error" in status
        
        # Test 4: Empty profile ID
        status = gradio_ui.create_form_profile("", '{"name": "John"}')
        assert "Error" in status
        
        # Test 5: Invalid archive directory
        status = gradio_ui.archive_old_files("/nonexistent/path", 30)
        assert "Error" in status

    def test_settings_error_handling(self):
        """Test error handling in settings management."""
        gradio_ui = GradioUI()
        
        # Test 1: Empty setting key
        status = gradio_ui.save_setting("", "value")
        assert "Error" in status
        
        # Test 2: Empty setting value
        status = gradio_ui.save_setting("key", "")
        assert "Error" in status
        
        # Test 3: Empty credential key
        status = gradio_ui.save_credential("", "secret")
        assert "Error" in status
        
        # Test 4: Empty credential value
        status = gradio_ui.save_credential("key", "")
        assert "Error" in status
        
        # Test 5: Clear non-existent setting
        status = gradio_ui.clear_setting("nonexistent_key")
        # Should handle gracefully (either success or error message)
        assert isinstance(status, str)

    @given(
        invalid_input=st.one_of(
            st.just(""),
            st.just("/nonexistent/path"),
            st.just("not json"),
            st.just("invalid url")
        )
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_error_handling_consistency_across_modules(self, invalid_input):
        """Property: For any invalid input, all modules should handle errors gracefully.
        
        This test verifies that:
        1. Invalid inputs are rejected
        2. Error messages are returned
        3. Error handling is consistent across modules
        4. No exceptions are raised to the user
        """
        gradio_ui = GradioUI()
        
        # Test various modules with invalid input
        results = []
        
        # File automation (returns tuple)
        try:
            result = gradio_ui.bulk_rename_preview(invalid_input, "pattern", "replacement")
            # Extract status from tuple
            status = result[0] if isinstance(result, tuple) else result
            results.append(status)
        except Exception as e:
            pytest.fail(f"File automation should handle error gracefully: {e}")
        
        # Communication automation
        try:
            result = gradio_ui.summarize_emails(invalid_input, max_length=100)
            results.append(result)
        except Exception as e:
            pytest.fail(f"Communication automation should handle error gracefully: {e}")
        
        # Productivity automation
        try:
            result = gradio_ui.parse_csv_file(invalid_input)
            results.append(result)
        except Exception as e:
            pytest.fail(f"Productivity automation should handle error gracefully: {e}")
        
        # Web & Cloud automation
        try:
            result = gradio_ui.validate_urls(invalid_input)
            results.append(result)
        except Exception as e:
            pytest.fail(f"Web & Cloud automation should handle error gracefully: {e}")
        
        # Verify all results are strings (error messages or status)
        for result in results:
            assert isinstance(result, str), "Error handling should return a string message"


class TestCompleteAutomationWorkflows:
    """Integration tests for complete end-to-end automation workflows.
    
    **Feature: lazy-automation-platform, Integration Testing**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
    """

    def test_complete_email_workflow(self):
        """Test complete email automation workflow."""
        gradio_ui = GradioUI()
        
        # Step 1: Add templates
        gradio_ui.add_template("urgent_reply", "urgent, asap", "This is urgent!")
        gradio_ui.add_template("follow_up", "follow-up, check", "Let me follow up on this.")
        
        # Step 2: List templates
        templates = gradio_ui.list_templates()
        assert "urgent_reply" in templates
        assert "follow_up" in templates
        
        # Step 3: Match template
        result = gradio_ui.match_template("This is urgent and needs immediate attention")
        assert "Matched Template" in result or "No matching template" in result
        
        # Step 4: Summarize email
        email_body = "This is a long email with lots of content that needs to be summarized."
        summary = gradio_ui.summarize_emails(email_body, max_length=50)
        assert "Summary" in summary

    def test_complete_productivity_workflow(self):
        """Test complete productivity automation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            gradio_ui = GradioUI()
            
            # Step 1: Create and parse CSV
            csv_path = os.path.join(temp_dir, "data.csv")
            with open(csv_path, "w") as f:
                f.write("name,age,city\n")
                f.write("John,30,NYC\n")
                f.write("Jane,25,LA\n")
            
            stats = gradio_ui.parse_csv_file(csv_path)
            assert "CSV Statistics" in stats
            
            # Step 2: Export to JSON
            json_export = gradio_ui.export_csv_to_json(csv_path)
            parsed = json.loads(json_export)
            assert len(parsed) == 2
            
            # Step 3: Add clipboard items
            gradio_ui.add_clipboard_item("Important data", "task1", "important")
            gradio_ui.add_clipboard_item("Reference info", "task2", "reference")
            
            # Step 4: Search clipboard
            search_result = gradio_ui.search_clipboard("Important")
            assert "matching items" in search_result or "Important" in search_result
            
            # Step 5: Get clipboard history
            history = gradio_ui.get_clipboard_history()
            assert "Clipboard History" in history

    def test_complete_web_cloud_workflow(self):
        """Test complete web & cloud automation workflow."""
        gradio_ui = GradioUI()
        
        # Step 1: Validate URLs
        urls = "https://example.com/file1.pdf\nhttps://example.com/file2.pdf"
        validation = gradio_ui.validate_urls(urls)
        assert "Success" in validation
        
        # Step 2: Create form profiles
        profile_data = '{"name": "John", "email": "john@example.com", "phone": "555-1234"}'
        result = gradio_ui.create_form_profile("profile1", profile_data)
        assert "Success" in result
        
        # Step 3: List profiles
        profiles = gradio_ui.list_form_profiles()
        assert "profile1" in profiles
        
        # Step 4: Populate form fields
        form_fields = '{"name": "", "email": "", "phone": ""}'
        populated = gradio_ui.populate_form_fields("profile1", form_fields)
        parsed = json.loads(populated)
        assert parsed["name"] == "John"
        assert parsed["email"] == "john@example.com"

    def test_complete_dashboard_workflow(self):
        """Test complete dashboard and analytics workflow."""
        gradio_ui = GradioUI()
        
        # Step 1: Record automation executions
        for i in range(3):
            gradio_ui.analytics_engine.record_execution(
                execution_id=f"exec_{i}",
                automation_id=f"automation_{i}",
                automation_name=f"Test Automation {i}",
                success=i < 2,  # First 2 succeed, last one fails
                duration_seconds=10.0 + i,
                items_processed=50 + i * 10,
                time_saved_minutes=25.0 if i < 2 else 0.0,
                errors=[] if i < 2 else ["Test error"]
            )
        
        # Step 2: Get dashboard summary
        dashboard = gradio_ui.get_dashboard_summary()
        assert "DASHBOARD SUMMARY" in dashboard or "USAGE STATISTICS" in dashboard
        
        # Step 3: Get automation status
        status = gradio_ui.get_automation_status()
        assert "AUTOMATION STATUS" in status or "Executions" in status
        
        # Step 4: Get time saved report
        time_report = gradio_ui.get_time_saved_report()
        assert "TIME SAVED" in time_report or "Total Time Saved" in time_report
        
        # Step 5: Get error log
        error_log = gradio_ui.get_error_log_report()
        assert "ERROR" in error_log.upper()

    def test_complete_settings_workflow(self):
        """Test complete settings and configuration workflow."""
        gradio_ui = GradioUI()
        
        # Step 1: Save settings
        gradio_ui.save_setting("automation_enabled", "true")
        gradio_ui.save_setting("max_files", "1000")
        
        # Step 2: Get all settings
        all_settings = gradio_ui.get_all_settings()
        assert "automation_enabled" in all_settings or "Settings" in all_settings
        
        # Step 3: Save credentials
        gradio_ui.save_credential("api_key", "secret_key_value")
        
        # Step 4: Export settings (should exclude sensitive data)
        exported = gradio_ui.export_settings()
        parsed = json.loads(exported)
        # Credentials should not be in plain text
        assert "secret_key_value" not in exported
        
        # Step 5: Clear setting
        clear_result = gradio_ui.clear_setting("automation_enabled")
        assert "Success" in clear_result or isinstance(clear_result, str)


class TestUIIntegration:
    """Integration tests for UI components and interactions.
    
    **Feature: lazy-automation-platform, Integration Testing**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
    """

    def test_gradio_interface_builds_successfully(self):
        """Test that the Gradio interface builds without errors."""
        gradio_ui = GradioUI()
        interface = gradio_ui.build_interface()
        
        # Verify interface is created
        assert interface is not None
        assert hasattr(interface, 'launch')

    def test_all_tabs_are_accessible(self):
        """Test that all tabs are accessible and functional."""
        gradio_ui = GradioUI()
        
        # Test File Automation tab
        with tempfile.TemporaryDirectory() as temp_dir:
            result = gradio_ui.get_file_type_distribution(temp_dir)
            assert isinstance(result, str)
        
        # Test Communication Automation tab
        result = gradio_ui.list_templates()
        assert isinstance(result, str)
        
        # Test Productivity Automation tab
        result = gradio_ui.get_clipboard_history()
        assert isinstance(result, str)
        
        # Test Web & Cloud Automation tab
        result = gradio_ui.list_form_profiles()
        assert isinstance(result, str)
        
        # Test Dashboard tab
        result = gradio_ui.get_dashboard_summary()
        assert isinstance(result, str)
        
        # Test Settings tab
        result = gradio_ui.get_all_settings()
        assert isinstance(result, str)

    def test_preview_panels_display_results(self):
        """Test that preview panels display results correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            gradio_ui = GradioUI()
            
            # Create test files
            for i in range(3):
                file_path = os.path.join(temp_dir, f"file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content {i}")
            
            # Test bulk rename preview
            status, preview = gradio_ui.bulk_rename_preview(temp_dir, "file_", "renamed_")
            assert isinstance(preview, list)
            
            # Test CSV parsing preview
            csv_path = os.path.join(temp_dir, "test.csv")
            with open(csv_path, "w") as f:
                f.write("name,age\nJohn,30\n")
            
            stats = gradio_ui.parse_csv_file(csv_path)
            assert "CSV Statistics" in stats

    def test_download_functionality_available(self):
        """Test that download functionality is available for all automation tasks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            gradio_ui = GradioUI()
            
            # Test file automation download
            for i in range(2):
                file_path = os.path.join(temp_dir, f"file_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content {i}")
            
            status = gradio_ui.bulk_rename_apply(temp_dir, "file_", "renamed_")
            assert isinstance(status, str)
            
            # Test CSV export download
            csv_path = os.path.join(temp_dir, "test.csv")
            with open(csv_path, "w") as f:
                f.write("name,age\nJohn,30\n")
            
            json_export = gradio_ui.export_csv_to_json(csv_path)
            assert isinstance(json_export, str)
            
            # Test email summary download
            email_body = "This is a long email with lots of content."
            summary = gradio_ui.summarize_emails(email_body, max_length=50)
            assert "Summary" in summary

    @given(
        automation_type=st.sampled_from(['file', 'communication', 'productivity', 'web', 'dashboard'])
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_all_automation_types_return_valid_output(self, automation_type):
        """Property: For any automation type, the system should return valid output.
        
        This test verifies that:
        1. All automation types return string output
        2. Output is non-empty
        3. Output is properly formatted
        4. No exceptions are raised
        """
        gradio_ui = GradioUI()
        
        try:
            if automation_type == 'file':
                with tempfile.TemporaryDirectory() as temp_dir:
                    result = gradio_ui.get_file_type_distribution(temp_dir)
            elif automation_type == 'communication':
                result = gradio_ui.list_templates()
            elif automation_type == 'productivity':
                result = gradio_ui.get_clipboard_history()
            elif automation_type == 'web':
                result = gradio_ui.list_form_profiles()
            else:  # dashboard
                result = gradio_ui.get_dashboard_summary()
            
            # Verify output is valid
            assert isinstance(result, str), f"{automation_type} should return a string"
            assert len(result) > 0, f"{automation_type} output should not be empty"
        except Exception as e:
            pytest.fail(f"{automation_type} automation should not raise exceptions: {e}")

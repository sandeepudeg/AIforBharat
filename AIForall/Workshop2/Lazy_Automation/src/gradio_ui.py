"""Gradio UI for the Lazy Automation Platform."""

import gradio as gr
import os
import json
import tempfile
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime
from src.file_automation import BulkRenamer, AutoOrganizer, DuplicateCleaner
from src.communication_automation import EmailSummarizer, TemplateResponder, NotificationBot
from src.productivity_automation import ReportGenerator, LogCleaner, ClipboardEnhancer
from src.web_cloud_automation import BulkDownloader, AutoFormFiller, CloudSyncCleanup
from src.config_manager import ConfigManager
from src.error_handler import ErrorHandler
from src.analytics_engine import AnalyticsEngine
from src.backup_manager import BackupManager
from src.task_scheduler import TaskScheduler
from src.workflow_chain import WorkflowChainEngine
from src.trigger_manager import TriggerManager
from src.rules_engine import RulesEngine
from src.data_models import CustomRule


class GradioUI:
    """Main Gradio application for the Lazy Automation Platform."""

    def __init__(self):
        """Initialize the Gradio UI with all modules."""
        self.config_manager = ConfigManager()
        self.error_handler = ErrorHandler()
        self.template_responder = TemplateResponder()
        self.notification_bot = NotificationBot()
        self.clipboard_enhancer = ClipboardEnhancer()
        self.form_filler = AutoFormFiller()
        self.cloud_cleanup = CloudSyncCleanup()
        self.analytics_engine = AnalyticsEngine()
        self.backup_manager = BackupManager()
        self.task_scheduler = TaskScheduler()
        self.workflow_engine = WorkflowChainEngine()
        self.trigger_manager = TriggerManager()
        self.rules_engine = RulesEngine()
        
        # Load saved configurations
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load saved configurations from persistent storage."""
        try:
            # Load any saved templates
            saved_templates = self.config_manager.load_config("templates")
            if saved_templates:
                for template_id, template_data in saved_templates.items():
                    self.template_responder.add_template(
                        template_id,
                        template_data.get("keywords", []),
                        template_data.get("response", "")
                    )
        except Exception:
            # If no saved templates, continue with empty templates
            pass

    # ==================== File Automation Tab ====================

    def bulk_rename_preview(self, directory: str, pattern: str, replacement: str) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Generate a preview of bulk rename operations.

        Args:
            directory: Directory containing files to rename
            pattern: Regex pattern to match
            replacement: Replacement string

        Returns:
            Tuple of (status_message, preview_list)
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory", []

            preview = BulkRenamer.generate_preview(directory, pattern, replacement)
            
            if not preview:
                return "No files match the pattern", []

            return f"Preview: {len(preview)} files will be renamed", preview
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}", []

    def bulk_rename_apply(self, directory: str, pattern: str, replacement: str) -> str:
        """
        Apply bulk rename operations.

        Args:
            directory: Directory containing files to rename
            pattern: Regex pattern to match
            replacement: Replacement string

        Returns:
            Status message
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            result = BulkRenamer.apply_rename(directory, pattern, replacement)
            
            if result.success:
                return f"Success: {result.processed_count} files renamed"
            else:
                return f"Completed with errors: {result.processed_count} renamed, {result.error_count} failed"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def auto_organize(self, directory: str) -> str:
        """
        Organize files by type into categorized subdirectories.

        Args:
            directory: Directory to organize

        Returns:
            Status message
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            result = AutoOrganizer.organize_files(directory, create_subdirs=True)
            
            if result.success:
                return f"Success: {result.processed_count} files organized"
            else:
                return f"Completed with errors: {result.processed_count} organized, {result.error_count} failed"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_file_type_distribution(self, directory: str) -> str:
        """
        Get distribution of file types in a directory.

        Args:
            directory: Directory to analyze

        Returns:
            Formatted distribution string
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            distribution = AutoOrganizer.get_file_type_distribution(directory)
            
            if not distribution:
                return "No files found in directory"

            result = "File Type Distribution:\n"
            for file_type, count in sorted(distribution.items()):
                result += f"  {file_type}: {count} files\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def find_duplicates(self, directory: str) -> str:
        """
        Find duplicate files in a directory.

        Args:
            directory: Directory to search

        Returns:
            Formatted duplicate summary
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            summary = DuplicateCleaner.get_duplicate_summary(directory)
            
            if summary["duplicate_groups"] == 0:
                return "No duplicates found"

            result = "Duplicate Summary:\n"
            result += f"  Duplicate Groups: {summary['duplicate_groups']}\n"
            result += f"  Duplicate Files: {summary['duplicate_files']}\n"
            result += f"  Space Saved: {summary['space_saved_mb']} MB\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def remove_duplicates(self, directory: str, keep_first: bool = True) -> str:
        """
        Remove duplicate files from a directory.

        Args:
            directory: Directory to clean
            keep_first: Whether to keep the first or last file

        Returns:
            Status message
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            result = DuplicateCleaner.remove_duplicates(directory, keep_first=keep_first)
            
            if result.success:
                return f"Success: {result.processed_count} duplicate files removed"
            else:
                return f"Completed with errors: {result.processed_count} removed, {result.error_count} failed"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Communication Automation Tab ====================

    def summarize_emails(self, email_body: str, max_length: int = 100) -> str:
        """
        Summarize email content.

        Args:
            email_body: The email body text
            max_length: Maximum summary length

        Returns:
            Summarized email
        """
        try:
            if not email_body or not email_body.strip():
                return "Error: Email body cannot be empty"

            summary = EmailSummarizer.summarize_email(email_body, max_length)
            
            return f"Original Length: {len(email_body)} chars\nSummary Length: {len(summary)} chars\n\nSummary:\n{summary}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def add_template(self, template_id: str, keywords: str, response: str) -> str:
        """
        Add a response template.

        Args:
            template_id: Unique template ID
            keywords: Comma-separated keywords
            response: Response text

        Returns:
            Status message
        """
        try:
            if not template_id or not template_id.strip():
                return "Error: Template ID cannot be empty"

            if not keywords or not keywords.strip():
                return "Error: Keywords cannot be empty"

            if not response or not response.strip():
                return "Error: Response cannot be empty"

            # Parse keywords
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
            
            if not keyword_list:
                return "Error: At least one keyword is required"

            self.template_responder.add_template(template_id, keyword_list, response)
            
            # Save to config
            templates = self.config_manager.load_config("templates") or {}
            templates[template_id] = {
                "keywords": keyword_list,
                "response": response
            }
            self.config_manager.save_config("templates", templates)
            
            return f"Success: Template '{template_id}' added with {len(keyword_list)} keywords"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def match_template(self, email_text: str) -> str:
        """
        Find a matching template for email text.

        Args:
            email_text: The email text to match

        Returns:
            Matched template response or message
        """
        try:
            if not email_text or not email_text.strip():
                return "Error: Email text cannot be empty"

            match = self.template_responder.find_matching_template(email_text)
            
            if match:
                template_id, response = match
                return f"Matched Template: {template_id}\n\nSuggested Response:\n{response}"
            else:
                return "No matching template found"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def list_templates(self) -> str:
        """
        List all stored templates.

        Returns:
            Formatted list of templates
        """
        try:
            templates = self.template_responder.get_all_templates()
            
            if not templates:
                return "No templates configured"

            result = "Configured Templates:\n"
            for template_id, template_data in templates.items():
                keywords = ", ".join(template_data["keywords"])
                result += f"\n  ID: {template_id}\n"
                result += f"  Keywords: {keywords}\n"
                result += f"  Response: {template_data['response'][:50]}...\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def add_reminder(self, reminder_id: str, event_name: str, event_time: str, channel: str) -> str:
        """
        Add a calendar reminder.

        Args:
            reminder_id: Unique reminder ID
            event_name: Name of the event
            event_time: Time of the event
            channel: Notification channel (slack, whatsapp, email)

        Returns:
            Status message
        """
        try:
            if not reminder_id or not reminder_id.strip():
                return "Error: Reminder ID cannot be empty"

            if not event_name or not event_name.strip():
                return "Error: Event name cannot be empty"

            if not event_time or not event_time.strip():
                return "Error: Event time cannot be empty"

            if not channel or not channel.strip():
                return "Error: Notification channel cannot be empty"

            self.notification_bot.add_reminder(reminder_id, event_name, event_time, channel)
            
            return f"Success: Reminder '{reminder_id}' added for {event_name}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def send_reminder(self, reminder_id: str) -> str:
        """
        Send a reminder notification.

        Args:
            reminder_id: ID of the reminder to send

        Returns:
            Status message
        """
        try:
            if not reminder_id or not reminder_id.strip():
                return "Error: Reminder ID cannot be empty"

            success = self.notification_bot.send_reminder(reminder_id)
            
            if success:
                return f"Success: Reminder '{reminder_id}' sent"
            else:
                return f"Error: Reminder '{reminder_id}' not found"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def list_reminders(self) -> str:
        """
        List all reminders.

        Returns:
            Formatted list of reminders
        """
        try:
            reminders = self.notification_bot.get_all_reminders()
            
            if not reminders:
                return "No reminders configured"

            result = "Configured Reminders:\n"
            for reminder_id, reminder_data in reminders.items():
                result += f"\n  ID: {reminder_id}\n"
                result += f"  Event: {reminder_data['event_name']}\n"
                result += f"  Time: {reminder_data['event_time']}\n"
                result += f"  Channel: {reminder_data['notification_channel']}\n"
                result += f"  Sent: {reminder_data['sent']}\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Productivity Automation Tab ====================

    def parse_csv_file(self, file_path: str) -> str:
        """
        Parse a CSV file and generate statistics.

        Args:
            file_path: Path to the CSV file

        Returns:
            Formatted statistics string
        """
        try:
            if not file_path or not os.path.isfile(file_path):
                return "Error: Invalid file path"

            headers, rows = ReportGenerator.parse_csv(file_path)
            stats = ReportGenerator.generate_statistics(headers, rows)

            result = "CSV Statistics:\n"
            result += f"  Rows: {stats['row_count']}\n"
            result += f"  Columns: {stats['column_count']}\n"
            result += f"  Numeric Columns: {', '.join(stats['numeric_columns']) or 'None'}\n"
            result += f"  Text Columns: {', '.join(stats['text_columns']) or 'None'}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def export_csv_to_json(self, file_path: str) -> str:
        """
        Export CSV file to JSON format.

        Args:
            file_path: Path to the CSV file

        Returns:
            JSON string or error message
        """
        try:
            if not file_path or not os.path.isfile(file_path):
                return "Error: Invalid file path"

            headers, rows = ReportGenerator.parse_csv(file_path)
            json_output = ReportGenerator.export_to_json(headers, rows)

            return json_output
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def analyze_log_file(self, file_path: str) -> str:
        """
        Analyze a log file for errors and warnings.

        Args:
            file_path: Path to the log file

        Returns:
            Formatted analysis string
        """
        try:
            if not file_path or not os.path.isfile(file_path):
                return "Error: Invalid file path"

            analysis = LogCleaner.analyze_log(file_path)

            result = "Log Analysis:\n"
            result += f"  Total Lines: {analysis['total_lines']}\n"
            result += f"  Errors: {analysis['error_count']}\n"
            result += f"  Warnings: {analysis['warning_count']}\n"

            if analysis['errors']:
                result += "\n  Top Errors:\n"
                for error in analysis['errors'][:5]:
                    result += f"    Line {error['line_number']}: {error['content'][:60]}...\n"

            if analysis['warnings']:
                result += "\n  Top Warnings:\n"
                for warning in analysis['warnings'][:5]:
                    result += f"    Line {warning['line_number']}: {warning['content'][:60]}...\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def add_clipboard_item(self, content: str, source_task: str = "", tags: str = "") -> str:
        """
        Add an item to clipboard history.

        Args:
            content: The clipboard content
            source_task: Optional source task identifier
            tags: Comma-separated tags

        Returns:
            Status message
        """
        try:
            if not content or not content.strip():
                return "Error: Content cannot be empty"

            tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

            self.clipboard_enhancer.add_item(content, source_task, tag_list)

            return f"Success: Item added to clipboard history"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def search_clipboard(self, query: str) -> str:
        """
        Search clipboard history.

        Args:
            query: Search query

        Returns:
            Formatted search results
        """
        try:
            if not query or not query.strip():
                return "Error: Query cannot be empty"

            results = self.clipboard_enhancer.search(query)

            if not results:
                return "No matching items found in clipboard history"

            result = f"Found {len(results)} matching items:\n"
            for idx, item in enumerate(results[:10], 1):
                result += f"\n  {idx}. {item['content'][:50]}...\n"
                result += f"     Time: {item['timestamp']}\n"
                if item['tags']:
                    result += f"     Tags: {', '.join(item['tags'])}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_clipboard_history(self) -> str:
        """
        Get the full clipboard history.

        Returns:
            Formatted clipboard history
        """
        try:
            history = self.clipboard_enhancer.get_history()

            if not history:
                return "Clipboard history is empty"

            result = f"Clipboard History ({len(history)} items):\n"
            for idx, item in enumerate(history[:20], 1):
                result += f"\n  {idx}. {item['content'][:50]}...\n"
                result += f"     Time: {item['timestamp']}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Web & Cloud Automation Tab ====================

    def validate_urls(self, urls_text: str) -> str:
        """
        Validate a list of URLs.

        Args:
            urls_text: Newline-separated URLs

        Returns:
            Validation result message
        """
        try:
            if not urls_text or not urls_text.strip():
                return "Error: URL list cannot be empty"

            urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

            if not urls:
                return "Error: No valid URLs provided"

            is_valid, error_msg = BulkDownloader.validate_urls(urls)

            if is_valid:
                return f"Success: All {len(urls)} URLs are valid"
            else:
                return f"Error: {error_msg}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def organize_downloads(self, directory: str, urls_text: str) -> str:
        """
        Organize downloaded files by type.

        Args:
            directory: Directory containing downloaded files
            urls_text: Newline-separated URLs (for reference)

        Returns:
            Status message
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            if not urls_text or not urls_text.strip():
                return "Error: URL list cannot be empty"

            urls = [url.strip() for url in urls_text.split("\n") if url.strip()]

            result = BulkDownloader.organize_downloads(directory, urls)

            if result.success:
                return f"Success: {result.processed_count} files organized"
            else:
                return f"Completed with errors: {result.processed_count} organized, {result.error_count} failed"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def create_form_profile(self, profile_id: str, profile_json: str) -> str:
        """
        Create a form filling profile.

        Args:
            profile_id: Unique profile identifier
            profile_json: JSON string with profile data

        Returns:
            Status message
        """
        try:
            if not profile_id or not profile_id.strip():
                return "Error: Profile ID cannot be empty"

            if not profile_json or not profile_json.strip():
                return "Error: Profile data cannot be empty"

            try:
                profile_data = json.loads(profile_json)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for profile data"

            if not isinstance(profile_data, dict):
                return "Error: Profile data must be a JSON object"

            self.form_filler.create_profile(profile_id, profile_data)

            return f"Success: Profile '{profile_id}' created with {len(profile_data)} fields"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def populate_form_fields(self, profile_id: str, form_fields_json: str) -> str:
        """
        Populate form fields using a stored profile.

        Args:
            profile_id: ID of the profile to use
            form_fields_json: JSON string with form field names

        Returns:
            Populated form fields as JSON
        """
        try:
            if not profile_id or not profile_id.strip():
                return "Error: Profile ID cannot be empty"

            if not form_fields_json or not form_fields_json.strip():
                return "Error: Form fields cannot be empty"

            try:
                form_fields = json.loads(form_fields_json)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for form fields"

            populated = self.form_filler.populate_form(profile_id, form_fields)

            return json.dumps(populated, indent=2)
        except KeyError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def list_form_profiles(self) -> str:
        """
        List all stored form profiles.

        Returns:
            Formatted list of profiles
        """
        try:
            profiles = self.form_filler.get_all_profiles()

            if not profiles:
                return "No form profiles configured"

            result = "Stored Form Profiles:\n"
            for profile_id, profile_data in profiles.items():
                result += f"\n  ID: {profile_id}\n"
                result += f"  Fields: {', '.join(profile_data.keys())}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def archive_old_files(self, directory: str, days_old: int) -> str:
        """
        Archive files older than specified number of days.

        Args:
            directory: Directory to scan
            days_old: Number of days to consider as "old"

        Returns:
            Status message
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            if not isinstance(days_old, int) or days_old < 0:
                return "Error: Days old must be a non-negative number"

            result = self.cloud_cleanup.archive_old_files(directory, days_old)

            if result.success:
                return f"Success: {result.processed_count} files archived"
            else:
                return f"Completed with errors: {result.processed_count} archived, {result.error_count} failed"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_archive_summary(self) -> str:
        """
        Get a summary of archived files.

        Returns:
            Formatted archive summary
        """
        try:
            summary = self.cloud_cleanup.get_archive_summary()

            result = "Archive Summary:\n"
            result += f"  Total Archived: {summary['total_archived']}\n"
            result += f"  Successful: {summary['successful']}\n"
            result += f"  Failed: {summary['failed']}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Dashboard Tab ====================

    def get_dashboard_summary(self) -> str:
        """
        Get dashboard summary with automation status and statistics.

        Returns:
            Formatted dashboard summary
        """
        try:
            summary = self.analytics_engine.get_dashboard_summary()
            
            result = "=== DASHBOARD SUMMARY ===\n\n"
            
            # Usage Statistics
            stats = summary.get("usage_statistics", {})
            result += "📊 USAGE STATISTICS\n"
            result += f"  Total Executions: {stats.get('total_executions', 0)}\n"
            result += f"  Successful: {stats.get('successful_executions', 0)}\n"
            result += f"  Failed: {stats.get('failed_executions', 0)}\n"
            result += f"  Success Rate: {stats.get('success_rate', 0)}%\n"
            result += f"  Total Items Processed: {stats.get('total_items_processed', 0)}\n"
            result += f"  Total Time Saved: {stats.get('total_time_saved_minutes', 0)} minutes\n"
            result += f"  Average Duration: {stats.get('average_duration_seconds', 0)} seconds\n\n"
            
            # Error Trends
            errors = summary.get("error_trends", {})
            result += "⚠️ ERROR TRENDS (Last 30 days)\n"
            result += f"  Total Errors: {errors.get('total_errors', 0)}\n"
            result += f"  Error Rate: {errors.get('error_rate', 0)}%\n"
            
            if errors.get("most_common_errors"):
                result += "  Most Common Errors:\n"
                for error_info in errors.get("most_common_errors", [])[:5]:
                    result += f"    - {error_info.get('error', 'Unknown')}: {error_info.get('count', 0)} times\n"
            result += "\n"
            
            # Automation Frequency
            frequency = summary.get("automation_frequency", {})
            if frequency:
                result += "🔄 MOST USED AUTOMATIONS\n"
                for auto_id, count in list(frequency.items())[:5]:
                    result += f"  {auto_id}: {count} executions\n"
                result += "\n"
            
            # Recent Executions
            recent = summary.get("recent_executions", [])
            if recent:
                result += "📝 RECENT EXECUTIONS\n"
                for exec_record in recent[:5]:
                    status = "✓" if exec_record.get("success") else "✗"
                    result += f"  {status} {exec_record.get('automation_name', 'Unknown')}\n"
                    result += f"     Time: {exec_record.get('timestamp', 'N/A')}\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_automation_status(self) -> str:
        """
        Get status of all configured automations.

        Returns:
            Formatted automation status
        """
        try:
            stats = self.analytics_engine.get_usage_statistics()
            automations = stats.get("automations", {})
            
            if not automations:
                return "No automations have been executed yet."
            
            result = "=== AUTOMATION STATUS ===\n\n"
            
            for auto_id, auto_stats in automations.items():
                result += f"📌 {auto_id}\n"
                result += f"  Status: {'Enabled' if auto_stats.get('executions', 0) > 0 else 'Idle'}\n"
                result += f"  Executions: {auto_stats.get('executions', 0)}\n"
                result += f"  Successful: {auto_stats.get('successful', 0)}\n"
                result += f"  Failed: {auto_stats.get('failed', 0)}\n"
                result += f"  Items Processed: {auto_stats.get('items_processed', 0)}\n"
                result += f"  Time Saved: {auto_stats.get('time_saved_minutes', 0)} minutes\n\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_automation_details(self, automation_id: str) -> str:
        """
        Get detailed information about a specific automation.

        Args:
            automation_id: ID of the automation to get details for

        Returns:
            Formatted automation details including last execution time, success rate, and configuration
        """
        try:
            if not automation_id or not automation_id.strip():
                return "Error: Automation ID cannot be empty"
            
            # Get execution history for this automation
            history = self.analytics_engine.get_execution_history(automation_id=automation_id, limit=100)
            
            if not history:
                return f"No execution history found for automation '{automation_id}'"
            
            # Calculate statistics
            total_executions = len(history)
            successful_executions = sum(1 for r in history if r.success)
            failed_executions = total_executions - successful_executions
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0.0
            
            # Get last execution details
            last_execution = history[0]  # Most recent is first
            
            # Calculate average metrics
            total_items = sum(r.items_processed for r in history)
            total_time_saved = sum(r.time_saved_minutes for r in history if r.success)
            avg_duration = sum(r.duration_seconds for r in history) / total_executions if total_executions > 0 else 0.0
            
            # Get configuration if available
            config = self.config_manager.load_config(f"automation_{automation_id}") or {}
            
            # Format the output
            result = f"=== AUTOMATION DETAILS: {automation_id} ===\n\n"
            
            result += "📊 EXECUTION STATISTICS\n"
            result += f"  Total Executions: {total_executions}\n"
            result += f"  Successful: {successful_executions}\n"
            result += f"  Failed: {failed_executions}\n"
            result += f"  Success Rate: {success_rate:.1f}%\n\n"
            
            result += "⏱️ PERFORMANCE METRICS\n"
            result += f"  Average Duration: {avg_duration:.2f} seconds\n"
            result += f"  Total Items Processed: {total_items}\n"
            result += f"  Total Time Saved: {total_time_saved:.2f} minutes\n\n"
            
            result += "🕐 LAST EXECUTION\n"
            result += f"  Time: {last_execution.timestamp}\n"
            result += f"  Status: {'✓ Success' if last_execution.success else '✗ Failed'}\n"
            result += f"  Duration: {last_execution.duration_seconds:.2f} seconds\n"
            result += f"  Items Processed: {last_execution.items_processed}\n"
            if last_execution.errors:
                result += f"  Errors: {', '.join(last_execution.errors[:3])}\n"
            result += "\n"
            
            result += "⚙️ CONFIGURATION\n"
            if config:
                for key, value in config.items():
                    # Mask sensitive values
                    if any(sensitive in key.lower() for sensitive in ['password', 'key', 'token', 'secret', 'credential']):
                        result += f"  {key}: [MASKED]\n"
                    else:
                        result += f"  {key}: {value}\n"
            else:
                result += "  No configuration stored\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_time_saved_report(self) -> str:
        """
        Get detailed time saved report.

        Returns:
            Formatted time saved report
        """
        try:
            stats = self.analytics_engine.get_usage_statistics()
            automations = stats.get("automations", {})
            
            result = "=== TIME SAVED REPORT ===\n\n"
            result += f"Total Time Saved: {stats.get('total_time_saved_minutes', 0)} minutes\n"
            result += f"  ({stats.get('total_time_saved_minutes', 0) / 60:.1f} hours)\n\n"
            
            result += "Time Saved by Automation:\n"
            sorted_autos = sorted(
                automations.items(),
                key=lambda x: x[1].get('time_saved_minutes', 0),
                reverse=True
            )
            
            for auto_id, auto_stats in sorted_autos[:10]:
                time_saved = auto_stats.get('time_saved_minutes', 0)
                if time_saved > 0:
                    result += f"  {auto_id}: {time_saved} minutes ({time_saved/60:.1f} hours)\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_error_log_report(self) -> str:
        """
        Get detailed error log report.

        Returns:
            Formatted error log report
        """
        try:
            errors = self.analytics_engine.get_error_trends()
            
            result = "=== ERROR LOG REPORT ===\n\n"
            result += f"Period: Last {errors.get('period_days', 30)} days\n"
            result += f"Total Errors: {errors.get('total_errors', 0)}\n"
            result += f"Error Rate: {errors.get('error_rate', 0)}%\n\n"
            
            errors_by_auto = errors.get('errors_by_automation', {})
            if errors_by_auto:
                result += "Errors by Automation:\n"
                for auto_id, error_count in sorted(errors_by_auto.items(), key=lambda x: x[1], reverse=True):
                    result += f"  {auto_id}: {error_count} errors\n"
                result += "\n"
            
            most_common = errors.get('most_common_errors', [])
            if most_common:
                result += "Most Common Errors:\n"
                for error_info in most_common[:10]:
                    result += f"  - {error_info.get('error', 'Unknown')}: {error_info.get('count', 0)} occurrences\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_undo_history(self) -> str:
        """
        Get undo history with available rollback options.

        Returns:
            Formatted undo history
        """
        try:
            history = self.backup_manager.get_undo_history(limit=20)
            
            if not history:
                return "No undo history available."
            
            result = "=== UNDO HISTORY ===\n\n"
            
            for idx, backup in enumerate(history, 1):
                result += f"{idx}. Backup ID: {backup.backup_id}\n"
                result += f"   Automation: {backup.automation_id}\n"
                result += f"   Time: {backup.timestamp}\n"
                result += f"   Files: {len(backup.affected_files)}\n"
                result += f"   Rollbackable: {'Yes' if backup.can_rollback else 'No'}\n\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def perform_undo(self, backup_id: str) -> str:
        """
        Perform an undo operation by restoring from backup.

        Args:
            backup_id: ID of the backup to restore

        Returns:
            Status message
        """
        try:
            if not backup_id or not backup_id.strip():
                return "Error: Backup ID cannot be empty"
            
            success, message = self.backup_manager.restore_backup(backup_id)
            
            if success:
                # Log the rollback
                self.backup_manager.log_rollback(backup_id, True)
                return f"Success: {message}"
            else:
                self.backup_manager.log_rollback(backup_id, False)
                return f"Error: {message}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Settings Tab ====================

    def get_all_settings(self) -> str:
        """
        Get all current settings.

        Returns:
            Formatted settings display
        """
        try:
            all_configs = self.config_manager.get_all_configs()
            
            if not all_configs:
                return "No settings configured yet."
            
            result = "=== CURRENT SETTINGS ===\n\n"
            
            for key, value in all_configs.items():
                # Mask sensitive keys
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret', 'credential']):
                    result += f"{key}: [MASKED]\n"
                else:
                    if isinstance(value, dict):
                        result += f"{key}: {json.dumps(value, indent=2)}\n"
                    else:
                        result += f"{key}: {value}\n"
            
            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def save_setting(self, setting_key: str, setting_value: str) -> str:
        """
        Save a configuration setting.

        Args:
            setting_key: Setting key
            setting_value: Setting value

        Returns:
            Status message
        """
        try:
            if not setting_key or not setting_key.strip():
                return "Error: Setting key cannot be empty"
            
            if not setting_value or not setting_value.strip():
                return "Error: Setting value cannot be empty"
            
            # Try to parse as JSON if it looks like JSON
            if setting_value.strip().startswith('{') or setting_value.strip().startswith('['):
                try:
                    parsed_value = json.loads(setting_value)
                    self.config_manager.save_config(setting_key, parsed_value)
                except json.JSONDecodeError:
                    self.config_manager.save_config(setting_key, setting_value)
            else:
                self.config_manager.save_config(setting_key, setting_value)
            
            return f"Success: Setting '{setting_key}' saved"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def save_credential(self, credential_key: str, credential_value: str) -> str:
        """
        Save an encrypted credential.

        Args:
            credential_key: Credential key
            credential_value: Credential value to encrypt

        Returns:
            Status message
        """
        try:
            if not credential_key or not credential_key.strip():
                return "Error: Credential key cannot be empty"
            
            if not credential_value or not credential_value.strip():
                return "Error: Credential value cannot be empty"
            
            self.config_manager.save_encrypted_credential(credential_key, credential_value)
            
            return f"Success: Credential '{credential_key}' saved and encrypted"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def clear_setting(self, setting_key: str) -> str:
        """
        Clear a configuration setting.

        Args:
            setting_key: Setting key to clear

        Returns:
            Status message
        """
        try:
            if not setting_key or not setting_key.strip():
                return "Error: Setting key cannot be empty"
            
            self.config_manager.clear_config(setting_key)
            
            return f"Success: Setting '{setting_key}' cleared"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def export_settings(self) -> str:
        """
        Export all settings (excluding sensitive data).

        Returns:
            JSON string of settings
        """
        try:
            all_configs = self.config_manager.get_all_configs()
            
            # Filter out sensitive data
            safe_configs = {}
            for key, value in all_configs.items():
                if not any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret', 'credential']):
                    safe_configs[key] = value
            
            return json.dumps(safe_configs, indent=2)
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Advanced Features Tab ====================

    def schedule_task(self, task_id: str, task_name: str, schedule: str) -> str:
        """
        Schedule an automation task.

        Args:
            task_id: Unique task identifier
            task_name: Human-readable task name
            schedule: Cron expression or interval (e.g., "0 9 * * *" for 9 AM daily)

        Returns:
            Status message
        """
        try:
            if not task_id or not task_id.strip():
                return "Error: Task ID cannot be empty"
            if not task_name or not task_name.strip():
                return "Error: Task name cannot be empty"
            if not schedule or not schedule.strip():
                return "Error: Schedule cannot be empty"

            # Create a dummy callback for now
            def dummy_callback():
                return f"Task {task_name} executed"

            scheduled_task = self.task_scheduler.schedule_task(
                task_id, task_name, schedule, dummy_callback, enabled=True
            )

            return f"Success: Task '{task_name}' scheduled with schedule: {schedule}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def list_scheduled_tasks(self) -> str:
        """
        List all scheduled tasks.

        Returns:
            Formatted list of scheduled tasks
        """
        try:
            tasks = self.task_scheduler.get_all_tasks()

            if not tasks:
                return "No scheduled tasks configured."

            result = "=== SCHEDULED TASKS ===\n\n"
            for task in tasks:
                result += f"📌 {task.task_name}\n"
                result += f"  ID: {task.task_id}\n"
                result += f"  Schedule: {task.schedule}\n"
                result += f"  Enabled: {'Yes' if task.enabled else 'No'}\n"
                result += f"  Executions: {task.execution_count}\n"
                if task.last_execution:
                    result += f"  Last Execution: {task.last_execution}\n"
                result += "\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def enable_scheduled_task(self, task_id: str) -> str:
        """
        Enable a scheduled task.

        Args:
            task_id: ID of the task to enable

        Returns:
            Status message
        """
        try:
            if not task_id or not task_id.strip():
                return "Error: Task ID cannot be empty"

            self.task_scheduler.enable_task(task_id)
            return f"Success: Task '{task_id}' enabled"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def disable_scheduled_task(self, task_id: str) -> str:
        """
        Disable a scheduled task.

        Args:
            task_id: ID of the task to disable

        Returns:
            Status message
        """
        try:
            if not task_id or not task_id.strip():
                return "Error: Task ID cannot be empty"

            self.task_scheduler.disable_task(task_id)
            return f"Success: Task '{task_id}' disabled"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def create_workflow_chain(self, chain_id: str, chain_name: str, tasks_json: str) -> str:
        """
        Create a workflow chain.

        Args:
            chain_id: Unique chain identifier
            chain_name: Human-readable chain name
            tasks_json: JSON array of task IDs

        Returns:
            Status message
        """
        try:
            if not chain_id or not chain_id.strip():
                return "Error: Chain ID cannot be empty"
            if not chain_name or not chain_name.strip():
                return "Error: Chain name cannot be empty"
            if not tasks_json or not tasks_json.strip():
                return "Error: Tasks cannot be empty"

            try:
                tasks = json.loads(tasks_json)
                if not isinstance(tasks, list):
                    return "Error: Tasks must be a JSON array"
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for tasks"

            chain = self.workflow_engine.create_chain(
                chain_id, chain_name, tasks, enabled=True
            )

            return f"Success: Workflow chain '{chain_name}' created with {len(tasks)} tasks"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def list_workflow_chains(self) -> str:
        """
        List all workflow chains.

        Returns:
            Formatted list of workflow chains
        """
        try:
            chains = self.workflow_engine.get_all_chains()

            if not chains:
                return "No workflow chains configured."

            result = "=== WORKFLOW CHAINS ===\n\n"
            for chain in chains:
                result += f"🔗 {chain.name}\n"
                result += f"  ID: {chain.chain_id}\n"
                result += f"  Tasks: {', '.join(chain.tasks)}\n"
                result += f"  Enabled: {'Yes' if chain.enabled else 'No'}\n"
                if chain.last_executed:
                    result += f"  Last Executed: {chain.last_executed}\n"
                result += "\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def execute_workflow_chain(self, chain_id: str) -> str:
        """
        Execute a workflow chain.

        Args:
            chain_id: ID of the chain to execute

        Returns:
            Status message with result
        """
        try:
            if not chain_id or not chain_id.strip():
                return "Error: Chain ID cannot be empty"

            success, result, error = self.workflow_engine.execute_chain(chain_id)

            if success:
                return f"Success: Workflow chain executed successfully\nResult: {result}"
            else:
                return f"Error: Workflow chain execution failed\n{error}"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def create_trigger(self, trigger_id: str, trigger_type: str, automation_id: str, config_json: str) -> str:
        """
        Create an event trigger.

        Args:
            trigger_id: Unique trigger identifier
            trigger_type: Type of trigger (new_email, file_added, time_based)
            automation_id: ID of automation to execute
            config_json: JSON configuration for the trigger

        Returns:
            Status message
        """
        try:
            if not trigger_id or not trigger_id.strip():
                return "Error: Trigger ID cannot be empty"
            if not trigger_type or not trigger_type.strip():
                return "Error: Trigger type cannot be empty"
            if not automation_id or not automation_id.strip():
                return "Error: Automation ID cannot be empty"
            if not config_json or not config_json.strip():
                return "Error: Configuration cannot be empty"

            try:
                config = json.loads(config_json)
                if not isinstance(config, dict):
                    return "Error: Configuration must be a JSON object"
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for configuration"

            # Register a dummy automation if not already registered
            if automation_id not in self.trigger_manager._automation_callbacks:
                def dummy_automation():
                    return f"Automation {automation_id} executed"
                self.trigger_manager.register_automation(automation_id, dummy_automation)

            trigger = self.trigger_manager.create_trigger(
                trigger_id, trigger_type, automation_id, config, enabled=True
            )

            return f"Success: Trigger '{trigger_id}' created (type: {trigger_type})"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def list_triggers(self) -> str:
        """
        List all triggers.

        Returns:
            Formatted list of triggers
        """
        try:
            triggers = self.trigger_manager.get_all_triggers()

            if not triggers:
                return "No triggers configured."

            result = "=== TRIGGERS ===\n\n"
            for trigger in triggers:
                result += f"⚡ {trigger.trigger_id}\n"
                result += f"  Type: {trigger.trigger_type.value}\n"
                result += f"  Automation: {trigger.automation_id}\n"
                result += f"  Enabled: {'Yes' if trigger.enabled else 'No'}\n"
                result += f"  Triggered: {trigger.trigger_count} times\n"
                if trigger.last_triggered:
                    result += f"  Last Triggered: {trigger.last_triggered}\n"
                result += "\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def enable_trigger(self, trigger_id: str) -> str:
        """
        Enable a trigger.

        Args:
            trigger_id: ID of the trigger to enable

        Returns:
            Status message
        """
        try:
            if not trigger_id or not trigger_id.strip():
                return "Error: Trigger ID cannot be empty"

            self.trigger_manager.enable_trigger(trigger_id)
            return f"Success: Trigger '{trigger_id}' enabled"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def disable_trigger(self, trigger_id: str) -> str:
        """
        Disable a trigger.

        Args:
            trigger_id: ID of the trigger to disable

        Returns:
            Status message
        """
        try:
            if not trigger_id or not trigger_id.strip():
                return "Error: Trigger ID cannot be empty"

            self.trigger_manager.disable_trigger(trigger_id)
            return f"Success: Trigger '{trigger_id}' disabled"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def create_custom_rule(self, rule_id: str, rule_name: str, conditions_json: str, actions_json: str) -> str:
        """
        Create a custom automation rule.

        Args:
            rule_id: Unique rule identifier
            rule_name: Human-readable rule name
            conditions_json: JSON object with conditions
            actions_json: JSON array with actions

        Returns:
            Status message
        """
        try:
            if not rule_id or not rule_id.strip():
                return "Error: Rule ID cannot be empty"
            if not rule_name or not rule_name.strip():
                return "Error: Rule name cannot be empty"
            if not conditions_json or not conditions_json.strip():
                return "Error: Conditions cannot be empty"
            if not actions_json or not actions_json.strip():
                return "Error: Actions cannot be empty"

            try:
                conditions = json.loads(conditions_json)
                actions = json.loads(actions_json)
                if not isinstance(actions, list):
                    return "Error: Actions must be a JSON array"
            except json.JSONDecodeError:
                return "Error: Invalid JSON format"

            rule = CustomRule(
                rule_id=rule_id,
                name=rule_name,
                conditions=conditions,
                actions=actions,
                enabled=True,
                execution_count=0
            )

            # Validate the rule
            is_valid, error_msg = self.rules_engine.validate_rule(rule)
            if not is_valid:
                return f"Error: {error_msg}"

            return f"Success: Custom rule '{rule_name}' created"
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def preview_custom_rule(self, rule_id: str, rule_name: str, conditions_json: str, actions_json: str, directory: str) -> str:
        """
        Preview a custom rule without applying it.

        Args:
            rule_id: Unique rule identifier
            rule_name: Human-readable rule name
            conditions_json: JSON object with conditions
            actions_json: JSON array with actions
            directory: Directory to apply rule to

        Returns:
            Preview of what would happen
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            try:
                conditions = json.loads(conditions_json)
                actions = json.loads(actions_json)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format"

            rule = CustomRule(
                rule_id=rule_id,
                name=rule_name,
                conditions=conditions,
                actions=actions,
                enabled=True,
                execution_count=0
            )

            # Apply rule in preview mode
            results = self.rules_engine.apply_rule(rule, directory, preview=True)

            result = f"=== RULE PREVIEW: {rule_name} ===\n\n"
            result += f"Matched Files: {results['total_matched']}\n"
            result += f"Would Execute: {results['total_executed']}\n"
            result += f"Potential Errors: {results['total_errors']}\n\n"

            if results['matched_files']:
                result += "Matched Files:\n"
                for file_path in results['matched_files'][:10]:
                    result += f"  - {file_path}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def apply_custom_rule(self, rule_id: str, rule_name: str, conditions_json: str, actions_json: str, directory: str) -> str:
        """
        Apply a custom rule to a directory.

        Args:
            rule_id: Unique rule identifier
            rule_name: Human-readable rule name
            conditions_json: JSON object with conditions
            actions_json: JSON array with actions
            directory: Directory to apply rule to

        Returns:
            Status message with results
        """
        try:
            if not directory or not os.path.isdir(directory):
                return "Error: Invalid directory"

            try:
                conditions = json.loads(conditions_json)
                actions = json.loads(actions_json)
            except json.JSONDecodeError:
                return "Error: Invalid JSON format"

            rule = CustomRule(
                rule_id=rule_id,
                name=rule_name,
                conditions=conditions,
                actions=actions,
                enabled=True,
                execution_count=0
            )

            # Apply rule
            results = self.rules_engine.apply_rule(rule, directory, preview=False)

            result = f"=== RULE EXECUTION: {rule_name} ===\n\n"
            result += f"Matched Files: {results['total_matched']}\n"
            result += f"Executed: {results['total_executed']}\n"
            result += f"Errors: {results['total_errors']}\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_undo_history_detailed(self) -> str:
        """
        Get detailed undo history with rollback options.

        Returns:
            Formatted undo history
        """
        try:
            history = self.backup_manager.get_undo_history(limit=20)

            if not history:
                return "No undo history available."

            result = "=== DETAILED UNDO HISTORY ===\n\n"

            for idx, backup in enumerate(history, 1):
                result += f"{idx}. Backup ID: {backup.backup_id}\n"
                result += f"   Automation: {backup.automation_id}\n"
                result += f"   Time: {backup.timestamp}\n"
                result += f"   Files Affected: {len(backup.affected_files)}\n"
                result += f"   Rollbackable: {'Yes' if backup.can_rollback else 'No'}\n"
                if backup.affected_files:
                    result += "   Files:\n"
                    for file_path in backup.affected_files[:3]:
                        result += f"     - {file_path}\n"
                    if len(backup.affected_files) > 3:
                        result += f"     ... and {len(backup.affected_files) - 3} more\n"
                result += "\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    def get_rollback_history(self) -> str:
        """
        Get rollback history.

        Returns:
            Formatted rollback history
        """
        try:
            history = self.backup_manager.get_rollback_history()

            if not history:
                return "No rollback history available."

            result = "=== ROLLBACK HISTORY ===\n\n"

            for idx, entry in enumerate(history[-20:], 1):  # Show last 20
                result += f"{idx}. Backup ID: {entry.get('backup_id', 'Unknown')}\n"
                result += f"   Automation: {entry.get('automation_id', 'Unknown')}\n"
                result += f"   Time: {entry.get('timestamp', 'Unknown')}\n"
                result += f"   Status: {'✓ Success' if entry.get('success') else '✗ Failed'}\n"
                result += f"   Files: {len(entry.get('affected_files', []))}\n\n"

            return result
        except Exception as e:
            error_msg = self.error_handler.handle_exception(e)
            return f"Error: {error_msg}"

    # ==================== Build Gradio Interface ====================

    def build_interface(self) -> gr.Blocks:
        """
        Build the complete Gradio interface with all tabs.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(title="Lazy Automation Platform") as interface:
            gr.Markdown("<h1 style='text-align: center; font-size: 3em;'>Lazy Automation Platform</h1>")
            gr.Markdown("<p style='text-align: center; font-size: 1.2em; color: #555;'>Automate repetitive tasks across file management, communication, and productivity</p>")

            with gr.Tabs():
                    # ==================== File Automation Tab ====================
                    with gr.Tab("File Automation"):
                        gr.Markdown("## File Automation Tools")
                        
                        with gr.Group():
                            gr.Markdown("### Bulk Rename")
                            with gr.Row():
                                file_dir_input = gr.Textbox(
                                    label="Directory Path",
                                    placeholder="/path/to/directory"
                                )
                            with gr.Row():
                                rename_pattern = gr.Textbox(
                                    label="Regex Pattern",
                                    placeholder="e.g., _old"
                                )
                                rename_replacement = gr.Textbox(
                                    label="Replacement",
                                    placeholder="e.g., _new"
                                )
                            with gr.Row():
                                rename_preview_btn = gr.Button("Preview Rename")
                                rename_apply_btn = gr.Button("Apply Rename", variant="primary")
                            
                            rename_output = gr.Textbox(
                                label="Status",
                                interactive=False
                            )
                            
                            rename_preview_btn.click(
                                self.bulk_rename_preview,
                                inputs=[file_dir_input, rename_pattern, rename_replacement],
                                outputs=[rename_output]
                            )
                            
                            rename_apply_btn.click(
                                self.bulk_rename_apply,
                                inputs=[file_dir_input, rename_pattern, rename_replacement],
                                outputs=[rename_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Auto-Organize")
                            with gr.Row():
                                organize_dir_input = gr.Textbox(
                                    label="Directory Path",
                                    placeholder="/path/to/directory"
                                )
                            with gr.Row():
                                organize_btn = gr.Button("Organize Files", variant="primary")
                                distribution_btn = gr.Button("Show Distribution")
                            
                            organize_output = gr.Textbox(
                                label="Status",
                                interactive=False
                            )
                            
                            organize_btn.click(
                                self.auto_organize,
                                inputs=[organize_dir_input],
                                outputs=[organize_output]
                            )
                            
                            distribution_btn.click(
                                self.get_file_type_distribution,
                                inputs=[organize_dir_input],
                                outputs=[organize_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Duplicate Cleaner")
                            with gr.Row():
                                dup_dir_input = gr.Textbox(
                                    label="Directory Path",
                                    placeholder="/path/to/directory"
                                )
                            with gr.Row():
                                find_dup_btn = gr.Button("Find Duplicates")
                                remove_dup_btn = gr.Button("Remove Duplicates", variant="primary")
                            with gr.Row():
                                keep_first = gr.Checkbox(
                                    label="Keep First File",
                                    value=True
                                )
                            
                            dup_output = gr.Textbox(
                                label="Status",
                                interactive=False
                            )
                            
                            find_dup_btn.click(
                                self.find_duplicates,
                                inputs=[dup_dir_input],
                                outputs=[dup_output]
                            )
                            
                            remove_dup_btn.click(
                                self.remove_duplicates,
                                inputs=[dup_dir_input, keep_first],
                                outputs=[dup_output]
                            )

                    # ==================== Communication Automation Tab ====================
                    with gr.Tab("Communication Automation"):
                        gr.Markdown("## Communication Automation Tools")
                        
                        with gr.Group():
                            gr.Markdown("### Email Summarizer")
                        with gr.Row():
                            email_body_input = gr.Textbox(
                                label="Email Body",
                                lines=5,
                                placeholder="Paste email content here"
                            )
                        with gr.Row():
                            email_max_length = gr.Slider(
                                label="Max Summary Length",
                                minimum=50,
                                maximum=500,
                                value=100,
                                step=10
                            )
                        with gr.Row():
                            summarize_btn = gr.Button("Summarize Email", variant="primary")
                        
                        email_output = gr.Textbox(
                            label="Summary Result",
                            interactive=False,
                            lines=5
                        )
                        
                        summarize_btn.click(
                            self.summarize_emails,
                            inputs=[email_body_input, email_max_length],
                            outputs=[email_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Template Responder")
                        with gr.Row():
                            template_id_input = gr.Textbox(
                                label="Template ID",
                                placeholder="e.g., urgent_reply"
                            )
                            template_keywords = gr.Textbox(
                                label="Keywords (comma-separated)",
                                placeholder="urgent, asap, important"
                            )
                        with gr.Row():
                            template_response = gr.Textbox(
                                label="Response Template",
                                lines=3,
                                placeholder="Your response text here"
                            )
                        with gr.Row():
                            add_template_btn = gr.Button("Add Template")
                            list_templates_btn = gr.Button("List Templates")
                        
                        template_output = gr.Textbox(
                            label="Result",
                            interactive=False,
                            lines=5
                        )
                        
                        add_template_btn.click(
                            self.add_template,
                            inputs=[template_id_input, template_keywords, template_response],
                            outputs=[template_output]
                        )
                        
                        list_templates_btn.click(
                            self.list_templates,
                            outputs=[template_output]
                        )

                        gr.Markdown("### Match Template")
                        with gr.Row():
                            match_email_input = gr.Textbox(
                                label="Email Text",
                                lines=3,
                                placeholder="Paste email to match against templates"
                            )
                        with gr.Row():
                            match_btn = gr.Button("Find Matching Template", variant="primary")
                        
                        match_output = gr.Textbox(
                            label="Match Result",
                            interactive=False,
                            lines=5
                        )
                        
                        match_btn.click(
                            self.match_template,
                            inputs=[match_email_input],
                            outputs=[match_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Notification Bot")
                        with gr.Row():
                            reminder_id_input = gr.Textbox(
                                label="Reminder ID",
                                placeholder="e.g., meeting_1"
                            )
                            event_name_input = gr.Textbox(
                                label="Event Name",
                                placeholder="e.g., Team Meeting"
                            )
                        with gr.Row():
                            event_time_input = gr.Textbox(
                                label="Event Time (ISO format)",
                                placeholder="2024-01-15T14:30:00"
                            )
                            channel_input = gr.Textbox(
                                label="Notification Channel",
                                placeholder="slack, whatsapp, or email"
                            )
                        with gr.Row():
                            add_reminder_btn = gr.Button("Add Reminder")
                            send_reminder_btn = gr.Button("Send Reminder", variant="primary")
                            list_reminders_btn = gr.Button("List Reminders")
                        
                        reminder_output = gr.Textbox(
                            label="Result",
                            interactive=False,
                            lines=5
                        )
                        
                        add_reminder_btn.click(
                            self.add_reminder,
                            inputs=[reminder_id_input, event_name_input, event_time_input, channel_input],
                            outputs=[reminder_output]
                        )
                        
                        send_reminder_btn.click(
                            self.send_reminder,
                            inputs=[reminder_id_input],
                            outputs=[reminder_output]
                        )
                        
                        list_reminders_btn.click(
                            self.list_reminders,
                            outputs=[reminder_output]
                        )

                    # ==================== Productivity Automation Tab ====================
                    with gr.Tab("Productivity Automation"):
                        gr.Markdown("## Productivity Automation Tools")
                        
                        with gr.Group():
                            gr.Markdown("### Report Generator")
                            with gr.Row():
                                csv_file_input = gr.Textbox(
                                    label="CSV File Path",
                                    placeholder="/path/to/file.csv"
                                )
                            with gr.Row():
                                parse_csv_btn = gr.Button("Parse CSV", variant="primary")
                                export_json_btn = gr.Button("Export to JSON")
                            
                            csv_output = gr.Textbox(
                                label="Result",
                                interactive=False,
                                lines=5
                            )
                            
                            parse_csv_btn.click(
                                self.parse_csv_file,
                                inputs=[csv_file_input],
                                outputs=[csv_output]
                            )
                            
                            export_json_btn.click(
                                self.export_csv_to_json,
                                inputs=[csv_file_input],
                                outputs=[csv_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Log Cleaner")
                            with gr.Row():
                                log_file_input = gr.Textbox(
                                    label="Log File Path",
                                    placeholder="/path/to/file.log"
                                )
                            with gr.Row():
                                analyze_log_btn = gr.Button("Analyze Log", variant="primary")
                            
                            log_output = gr.Textbox(
                                label="Analysis Result",
                                interactive=False,
                                lines=8
                            )
                            
                            analyze_log_btn.click(
                                self.analyze_log_file,
                                inputs=[log_file_input],
                                outputs=[log_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Clipboard Enhancer")
                            with gr.Row():
                                clipboard_content = gr.Textbox(
                                    label="Content to Add",
                                    lines=3,
                                    placeholder="Paste content here"
                                )
                            with gr.Row():
                                clipboard_source = gr.Textbox(
                                    label="Source Task (optional)",
                                    placeholder="e.g., email_summary"
                                )
                                clipboard_tags = gr.Textbox(
                                    label="Tags (comma-separated, optional)",
                                    placeholder="important, urgent"
                                )
                            with gr.Row():
                                add_clipboard_btn = gr.Button("Add to History")
                                search_clipboard_btn = gr.Button("Search History")
                                view_history_btn = gr.Button("View History")
                            
                            clipboard_query = gr.Textbox(
                                label="Search Query",
                                placeholder="Search term"
                            )
                            
                            clipboard_output = gr.Textbox(
                                label="Result",
                                interactive=False,
                                lines=8
                            )
                            
                            add_clipboard_btn.click(
                                self.add_clipboard_item,
                                inputs=[clipboard_content, clipboard_source, clipboard_tags],
                                outputs=[clipboard_output]
                            )
                            
                            search_clipboard_btn.click(
                                self.search_clipboard,
                                inputs=[clipboard_query],
                                outputs=[clipboard_output]
                            )
                            
                            view_history_btn.click(
                                self.get_clipboard_history,
                                outputs=[clipboard_output]
                            )

                    # ==================== Web & Cloud Automation Tab ====================
                    with gr.Tab("Web & Cloud Automation"):
                        gr.Markdown("## Web & Cloud Automation Tools")
                        
                        with gr.Group():
                            gr.Markdown("### Bulk Downloader")
                            with gr.Row():
                                urls_input = gr.Textbox(
                                    label="URLs (one per line)",
                                    lines=5,
                                    placeholder="https://example.com/file1.pdf\nhttps://example.com/file2.pdf"
                                )
                            with gr.Row():
                                validate_urls_btn = gr.Button("Validate URLs")
                            
                            urls_output = gr.Textbox(
                                label="Validation Result",
                                interactive=False
                            )
                            
                            validate_urls_btn.click(
                                self.validate_urls,
                                inputs=[urls_input],
                                outputs=[urls_output]
                            )

                            gr.Markdown("### Organize Downloads")
                            with gr.Row():
                                download_dir_input = gr.Textbox(
                                    label="Downloads Directory",
                                    placeholder="/path/to/downloads"
                                )
                            with gr.Row():
                                organize_downloads_btn = gr.Button("Organize Downloads", variant="primary")
                            
                            organize_output = gr.Textbox(
                                label="Organization Result",
                                interactive=False
                            )
                            
                            organize_downloads_btn.click(
                                self.organize_downloads,
                                inputs=[download_dir_input, urls_input],
                                outputs=[organize_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Auto Form Filler")
                            with gr.Row():
                                profile_id_input = gr.Textbox(
                                    label="Profile ID",
                                    placeholder="e.g., my_profile"
                                )
                            with gr.Row():
                                profile_data_input = gr.Textbox(
                                    label="Profile Data (JSON)",
                                    lines=4,
                                    placeholder='{"name": "John", "email": "john@example.com"}'
                                )
                            with gr.Row():
                                create_profile_btn = gr.Button("Create Profile")
                                list_profiles_btn = gr.Button("List Profiles")
                            
                            profile_output = gr.Textbox(
                                label="Result",
                                interactive=False,
                                lines=5
                            )
                            
                            create_profile_btn.click(
                                self.create_form_profile,
                                inputs=[profile_id_input, profile_data_input],
                                outputs=[profile_output]
                            )
                            
                            list_profiles_btn.click(
                                self.list_form_profiles,
                                outputs=[profile_output]
                            )

                            gr.Markdown("### Populate Form Fields")
                            with gr.Row():
                                form_fields_input = gr.Textbox(
                                    label="Form Fields (JSON)",
                                    lines=3,
                                    placeholder='{"name": "", "email": ""}'
                                )
                            with gr.Row():
                                populate_form_btn = gr.Button("Populate Form", variant="primary")
                            
                            form_output = gr.Textbox(
                                label="Populated Fields (JSON)",
                                interactive=False,
                                lines=5
                            )
                            
                            populate_form_btn.click(
                                self.populate_form_fields,
                                inputs=[profile_id_input, form_fields_input],
                                outputs=[form_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Cloud Sync Cleanup")
                            with gr.Row():
                                cloud_dir_input = gr.Textbox(
                                    label="Cloud Storage Directory",
                                    placeholder="/path/to/cloud/storage"
                                )
                            with gr.Row():
                                days_old_input = gr.Slider(
                                    label="Archive Files Older Than (days)",
                                    minimum=1,
                                    maximum=365,
                                    value=30,
                                    step=1
                                )
                            with gr.Row():
                                archive_btn = gr.Button("Archive Old Files", variant="primary")
                                summary_btn = gr.Button("View Archive Summary")
                            
                            cloud_output = gr.Textbox(
                                label="Result",
                                interactive=False,
                                lines=5
                            )
                            
                            archive_btn.click(
                                self.archive_old_files,
                                inputs=[cloud_dir_input, days_old_input],
                                outputs=[cloud_output]
                            )
                            
                            summary_btn.click(
                                self.get_archive_summary,
                                outputs=[cloud_output]
                            )

                    # ==================== Dashboard Tab ====================
                    with gr.Tab("Dashboard"):
                        gr.Markdown("## Dashboard & Analytics")
                        
                        with gr.Group():
                            gr.Markdown("### Dashboard Summary")
                            with gr.Row():
                                refresh_dashboard_btn = gr.Button("Refresh Dashboard", variant="primary")
                            
                            dashboard_output = gr.Textbox(
                                label="Dashboard Summary",
                                interactive=False,
                                lines=15
                            )
                            
                            refresh_dashboard_btn.click(
                                self.get_dashboard_summary,
                                outputs=[dashboard_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Automation Status")
                            with gr.Row():
                                status_btn = gr.Button("Show Status")
                            
                            status_output = gr.Textbox(
                                label="Automation Status",
                                interactive=False,
                                lines=12
                            )
                            
                            status_btn.click(
                                self.get_automation_status,
                                outputs=[status_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Time Saved Report")
                            with gr.Row():
                                time_saved_btn = gr.Button("Show Time Saved")
                            
                            time_saved_output = gr.Textbox(
                                label="Time Saved Report",
                                interactive=False,
                                lines=10
                            )
                            
                            time_saved_btn.click(
                                self.get_time_saved_report,
                                outputs=[time_saved_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Error Log Report")
                            with gr.Row():
                                error_log_btn = gr.Button("Show Error Log")
                            
                            error_log_output = gr.Textbox(
                                label="Error Log Report",
                                interactive=False,
                                lines=12
                            )
                            
                            error_log_btn.click(
                                self.get_error_log_report,
                                outputs=[error_log_output]
                            )

                        with gr.Group():
                            gr.Markdown("### Undo & Rollback")
                            with gr.Row():
                                history_btn = gr.Button("Show Undo History")
                            
                            undo_history_output = gr.Textbox(
                                label="Undo History",
                                interactive=False,
                                lines=10
                            )
                            
                            history_btn.click(
                                self.get_undo_history,
                                outputs=[undo_history_output]
                            )

                            gr.Markdown("### Perform Undo")
                            with gr.Row():
                                backup_id_input = gr.Textbox(
                                    label="Backup ID",
                                    placeholder="Enter backup ID to restore"
                                )
                            with gr.Row():
                                undo_btn = gr.Button("Perform Undo", variant="primary")
                            
                            undo_output = gr.Textbox(
                                label="Undo Result",
                                interactive=False
                            )
                            
                            undo_btn.click(
                                self.perform_undo,
                                inputs=[backup_id_input],
                                outputs=[undo_output]
                            )

                    # ==================== Advanced Features Tab ====================
                    with gr.Tab("Advanced"):
                        gr.Markdown("## Advanced Automation Features")
                        
                        with gr.Group():
                            gr.Markdown("### Task Scheduling")
                            with gr.Row():
                                task_id_input = gr.Textbox(
                                    label="Task ID",
                                    placeholder="e.g., daily_cleanup"
                                )
                                task_name_input = gr.Textbox(
                                    label="Task Name",
                                    placeholder="e.g., Daily Cleanup"
                                )
                            with gr.Row():
                                schedule_input = gr.Textbox(
                                    label="Schedule (Cron or Interval)",
                                    placeholder="e.g., 0 9 * * * (9 AM daily) or 'daily'"
                                )
                            with gr.Row():
                                schedule_btn = gr.Button("Schedule Task")
                                list_tasks_btn = gr.Button("List Scheduled Tasks")
                            
                            schedule_output = gr.Textbox(
                                label="Result",
                                interactive=False,
                                lines=8
                            )
                            
                            schedule_btn.click(
                                self.schedule_task,
                                inputs=[task_id_input, task_name_input, schedule_input],
                                outputs=[schedule_output]
                            )
                            
                            list_tasks_btn.click(
                                self.list_scheduled_tasks,
                                outputs=[schedule_output]
                            )

                            gr.Markdown("### Manage Scheduled Tasks")
                            with gr.Row():
                                manage_task_id = gr.Textbox(
                                    label="Task ID",
                                    placeholder="Enter task ID"
                                )
                            with gr.Row():
                                enable_task_btn = gr.Button("Enable Task")
                                disable_task_btn = gr.Button("Disable Task")
                            
                            manage_output = gr.Textbox(
                                label="Result",
                                interactive=False
                            )
                            
                            enable_task_btn.click(
                                self.enable_scheduled_task,
                                inputs=[manage_task_id],
                                outputs=[manage_output]
                            )
                            
                            disable_task_btn.click(
                                self.disable_scheduled_task,
                                inputs=[manage_task_id],
                                outputs=[manage_output]
                            )

                    with gr.Group():
                        gr.Markdown("### Workflow Chaining")
                        with gr.Row():
                            chain_id_input = gr.Textbox(
                                label="Chain ID",
                                placeholder="e.g., cleanup_chain"
                            )
                            chain_name_input = gr.Textbox(
                                label="Chain Name",
                                placeholder="e.g., Cleanup Workflow"
                            )
                        with gr.Row():
                            chain_tasks_input = gr.Textbox(
                                label="Tasks (JSON array)",
                                lines=3,
                                placeholder='["task1", "task2", "task3"]'
                            )
                        with gr.Row():
                            create_chain_btn = gr.Button("Create Chain")
                            list_chains_btn = gr.Button("List Chains")
                        
                        chain_output = gr.Textbox(
                            label="Result",
                            interactive=False,
                            lines=8
                        )
                        
                        create_chain_btn.click(
                            self.create_workflow_chain,
                            inputs=[chain_id_input, chain_name_input, chain_tasks_input],
                            outputs=[chain_output]
                        )
                        
                        list_chains_btn.click(
                            self.list_workflow_chains,
                            outputs=[chain_output]
                        )

                        gr.Markdown("### Execute Workflow Chain")
                        with gr.Row():
                            exec_chain_id = gr.Textbox(
                                label="Chain ID",
                                placeholder="Enter chain ID to execute"
                            )
                        with gr.Row():
                            exec_chain_btn = gr.Button("Execute Chain", variant="primary")
                        
                        exec_output = gr.Textbox(
                            label="Execution Result",
                            interactive=False,
                            lines=6
                        )
                        
                        exec_chain_btn.click(
                            self.execute_workflow_chain,
                            inputs=[exec_chain_id],
                            outputs=[exec_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Event Triggers")
                        with gr.Row():
                            trigger_id_input = gr.Textbox(
                                label="Trigger ID",
                                placeholder="e.g., new_email_trigger"
                            )
                            trigger_type_input = gr.Textbox(
                                label="Trigger Type",
                                placeholder="new_email, file_added, or time_based"
                            )
                        with gr.Row():
                            trigger_automation_input = gr.Textbox(
                                label="Automation ID",
                                placeholder="ID of automation to execute"
                            )
                        with gr.Row():
                            trigger_config_input = gr.Textbox(
                                label="Configuration (JSON)",
                                lines=3,
                                placeholder='{"watch_path": "/path/to/watch"}'
                            )
                        with gr.Row():
                            create_trigger_btn = gr.Button("Create Trigger")
                            list_triggers_btn = gr.Button("List Triggers")
                        
                        trigger_output = gr.Textbox(
                            label="Result",
                            interactive=False,
                            lines=8
                        )
                        
                        create_trigger_btn.click(
                            self.create_trigger,
                            inputs=[trigger_id_input, trigger_type_input, trigger_automation_input, trigger_config_input],
                            outputs=[trigger_output]
                        )
                        
                        list_triggers_btn.click(
                            self.list_triggers,
                            outputs=[trigger_output]
                        )

                        gr.Markdown("### Manage Triggers")
                        with gr.Row():
                            manage_trigger_id = gr.Textbox(
                                label="Trigger ID",
                                placeholder="Enter trigger ID"
                            )
                        with gr.Row():
                            enable_trigger_btn = gr.Button("Enable Trigger")
                            disable_trigger_btn = gr.Button("Disable Trigger")
                        
                        manage_trigger_output = gr.Textbox(
                            label="Result",
                            interactive=False
                        )
                        
                        enable_trigger_btn.click(
                            self.enable_trigger,
                            inputs=[manage_trigger_id],
                            outputs=[manage_trigger_output]
                        )
                        
                        disable_trigger_btn.click(
                            self.disable_trigger,
                            inputs=[manage_trigger_id],
                            outputs=[manage_trigger_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Custom Rules Engine")
                        with gr.Row():
                            rule_id_input = gr.Textbox(
                                label="Rule ID",
                                placeholder="e.g., old_files_rule"
                            )
                            rule_name_input = gr.Textbox(
                                label="Rule Name",
                                placeholder="e.g., Archive Old Files"
                            )
                        with gr.Row():
                            rule_conditions_input = gr.Textbox(
                                label="Conditions (JSON)",
                                lines=3,
                                placeholder='{"file_age": {"type": "file_age", "operator": ">", "value": 30}}'
                            )
                        with gr.Row():
                            rule_actions_input = gr.Textbox(
                                label="Actions (JSON array)",
                                lines=3,
                                placeholder='[{"type": "move", "destination": "/archive"}]'
                            )
                        with gr.Row():
                            rule_directory_input = gr.Textbox(
                                label="Directory to Apply Rule",
                                placeholder="/path/to/directory"
                            )
                        with gr.Row():
                            preview_rule_btn = gr.Button("Preview Rule")
                            apply_rule_btn = gr.Button("Apply Rule", variant="primary")
                        
                        rule_output = gr.Textbox(
                            label="Result",
                            interactive=False,
                            lines=10
                        )
                        
                        preview_rule_btn.click(
                            self.preview_custom_rule,
                            inputs=[rule_id_input, rule_name_input, rule_conditions_input, rule_actions_input, rule_directory_input],
                            outputs=[rule_output]
                        )
                        
                        apply_rule_btn.click(
                            self.apply_custom_rule,
                            inputs=[rule_id_input, rule_name_input, rule_conditions_input, rule_actions_input, rule_directory_input],
                            outputs=[rule_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Undo & Rollback Management")
                        with gr.Row():
                            undo_history_btn = gr.Button("View Undo History")
                            rollback_history_btn = gr.Button("View Rollback History")
                        
                        history_output = gr.Textbox(
                            label="History",
                            interactive=False,
                            lines=12
                        )
                        
                        undo_history_btn.click(
                            self.get_undo_history_detailed,
                            outputs=[history_output]
                        )
                        
                        rollback_history_btn.click(
                            self.get_rollback_history,
                            outputs=[history_output]
                        )

                    # ==================== Settings Tab ====================
                    with gr.Tab("Settings"):
                        gr.Markdown("## Configuration & Settings")
                        
                        with gr.Group():
                            gr.Markdown("### View Current Settings")
                            with gr.Row():
                                view_settings_btn = gr.Button("View All Settings")
                        
                        settings_output = gr.Textbox(
                            label="Current Settings",
                            interactive=False,
                            lines=12
                        )
                        
                        view_settings_btn.click(
                            self.get_all_settings,
                            outputs=[settings_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Save Setting")
                        with gr.Row():
                            setting_key_input = gr.Textbox(
                                label="Setting Key",
                                placeholder="e.g., api_timeout"
                            )
                        with gr.Row():
                            setting_value_input = gr.Textbox(
                                label="Setting Value",
                                lines=2,
                                placeholder="e.g., 30 or {\"key\": \"value\"}"
                            )
                        with gr.Row():
                            save_setting_btn = gr.Button("Save Setting", variant="primary")
                        
                        setting_output = gr.Textbox(
                            label="Result",
                            interactive=False
                        )
                        
                        save_setting_btn.click(
                            self.save_setting,
                            inputs=[setting_key_input, setting_value_input],
                            outputs=[setting_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Save Credential")
                        with gr.Row():
                            credential_key_input = gr.Textbox(
                                label="Credential Key",
                                placeholder="e.g., email_password"
                            )
                        with gr.Row():
                            credential_value_input = gr.Textbox(
                                label="Credential Value",
                                type="password",
                                placeholder="Enter credential (will be encrypted)"
                            )
                        with gr.Row():
                            save_credential_btn = gr.Button("Save Credential", variant="primary")
                        
                        credential_output = gr.Textbox(
                            label="Result",
                            interactive=False
                        )
                        
                        save_credential_btn.click(
                            self.save_credential,
                            inputs=[credential_key_input, credential_value_input],
                            outputs=[credential_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Clear Setting")
                        with gr.Row():
                            clear_key_input = gr.Textbox(
                                label="Setting Key to Clear",
                                placeholder="e.g., api_timeout"
                            )
                        with gr.Row():
                            clear_setting_btn = gr.Button("Clear Setting")
                        
                        clear_output = gr.Textbox(
                            label="Result",
                            interactive=False
                        )
                        
                        clear_setting_btn.click(
                            self.clear_setting,
                            inputs=[clear_key_input],
                            outputs=[clear_output]
                        )

                    with gr.Group():
                        gr.Markdown("### Export Settings")
                        with gr.Row():
                            export_settings_btn = gr.Button("Export Settings (Safe)")
                        
                        export_output = gr.Textbox(
                            label="Exported Settings (JSON)",
                            interactive=False,
                            lines=10
                        )
                        
                        export_settings_btn.click(
                            self.export_settings,
                            outputs=[export_output]
                        )

        return interface


def create_app() -> gr.Blocks:
    """
    Create and return the Gradio application.

    Returns:
        Gradio Blocks interface
    """
    ui = GradioUI()
    return ui.build_interface()


if __name__ == "__main__":
    app = create_app()
    app.launch()

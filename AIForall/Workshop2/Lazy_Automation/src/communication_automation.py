"""Communication automation module for email, templates, and notifications."""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from src.data_models import EmailSummary


class EmailSummarizer:
    """Handles email retrieval and summarization."""

    @staticmethod
    def summarize_email(email_body: str, max_length: int = 100) -> str:
        """
        Generate a concise summary of email content.

        Args:
            email_body: The full email body text
            max_length: Maximum length of the summary in characters

        Returns:
            Summarized email text

        Raises:
            ValueError: If email_body is empty or max_length is invalid
        """
        if not isinstance(email_body, str) or not email_body.strip():
            raise ValueError("email_body must be a non-empty string")

        if not isinstance(max_length, int) or max_length < 1:
            raise ValueError("max_length must be a positive integer")

        # Remove extra whitespace and normalize
        normalized = ' '.join(email_body.split())

        # If already shorter than max_length, return as is
        if len(normalized) <= max_length:
            return normalized

        # Simple summarization: take first sentences up to max_length
        sentences = re.split(r'(?<=[.!?])\s+', normalized)
        summary = ""

        for sentence in sentences:
            if len(summary) + len(sentence) + 1 <= max_length:
                if summary:
                    summary += " " + sentence
                else:
                    summary = sentence
            else:
                break

        # If summary is still empty, truncate the first sentence
        if not summary:
            summary = normalized[:max_length]

        return summary

    @staticmethod
    def create_email_summary(sender: str, subject: str, email_body: str, max_summary_length: int = 100) -> EmailSummary:
        """
        Create an EmailSummary object from email components.

        Args:
            sender: Email sender address
            subject: Email subject line
            email_body: Full email body text
            max_summary_length: Maximum length of the summary

        Returns:
            EmailSummary object

        Raises:
            ValueError: If any parameter is invalid
        """
        if not isinstance(sender, str) or not sender.strip():
            raise ValueError("sender must be a non-empty string")

        if not isinstance(subject, str):
            raise ValueError("subject must be a string")

        if not isinstance(email_body, str) or not email_body.strip():
            raise ValueError("email_body must be a non-empty string")

        summary_text = EmailSummarizer.summarize_email(email_body, max_summary_length)

        return EmailSummary(
            sender=sender,
            subject=subject,
            summary=summary_text,
            original_length=len(email_body),
            summary_length=len(summary_text)
        )

    @staticmethod
    def batch_summarize_emails(emails: List[Dict[str, str]], max_summary_length: int = 100) -> List[EmailSummary]:
        """
        Summarize multiple emails.

        Args:
            emails: List of email dictionaries with 'sender', 'subject', 'body' keys
            max_summary_length: Maximum length of each summary

        Returns:
            List of EmailSummary objects

        Raises:
            ValueError: If emails list is invalid
        """
        if not isinstance(emails, list):
            raise ValueError("emails must be a list")

        if len(emails) == 0:
            raise ValueError("emails list cannot be empty")

        summaries = []
        for email in emails:
            if not isinstance(email, dict):
                raise ValueError("Each email must be a dictionary")

            if 'sender' not in email or 'subject' not in email or 'body' not in email:
                raise ValueError("Each email must have 'sender', 'subject', and 'body' keys")

            summary = EmailSummarizer.create_email_summary(
                sender=email['sender'],
                subject=email['subject'],
                email_body=email['body'],
                max_summary_length=max_summary_length
            )
            summaries.append(summary)

        return summaries


class TemplateResponder:
    """Handles template matching and response suggestion."""

    def __init__(self):
        """Initialize the TemplateResponder with empty templates."""
        self.templates: Dict[str, Dict[str, str]] = {}

    def add_template(self, template_id: str, keywords: List[str], response: str) -> None:
        """
        Add a response template with trigger keywords.

        Args:
            template_id: Unique identifier for the template
            keywords: List of keywords that trigger this template
            response: The response text to suggest

        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(template_id, str) or not template_id.strip():
            raise ValueError("template_id must be a non-empty string")

        if not isinstance(keywords, list) or len(keywords) == 0:
            raise ValueError("keywords must be a non-empty list")

        if not all(isinstance(k, str) and k.strip() for k in keywords):
            raise ValueError("all keywords must be non-empty strings")

        if not isinstance(response, str) or not response.strip():
            raise ValueError("response must be a non-empty string")

        self.templates[template_id] = {
            'keywords': [k.lower() for k in keywords],
            'response': response
        }

    def find_matching_template(self, email_text: str) -> Optional[Tuple[str, str]]:
        """
        Find a matching template for the given email text.

        Args:
            email_text: The email text to match against templates

        Returns:
            Tuple of (template_id, response) if match found, None otherwise

        Raises:
            ValueError: If email_text is invalid
        """
        if not isinstance(email_text, str) or not email_text.strip():
            raise ValueError("email_text must be a non-empty string")

        email_lower = email_text.lower()

        # Find the first template that matches
        for template_id, template_data in self.templates.items():
            keywords = template_data['keywords']
            response = template_data['response']

            # Check if any keyword is in the email text
            for keyword in keywords:
                if keyword in email_lower:
                    return (template_id, response)

        return None

    def get_all_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get all stored templates.

        Returns:
            Dictionary of all templates
        """
        return self.templates.copy()

    def remove_template(self, template_id: str) -> bool:
        """
        Remove a template by ID.

        Args:
            template_id: ID of the template to remove

        Returns:
            True if template was removed, False if not found
        """
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False

    def clear_templates(self) -> None:
        """Clear all templates."""
        self.templates.clear()


class NotificationBot:
    """Handles calendar integration and reminder notifications."""

    def __init__(self):
        """Initialize the NotificationBot."""
        self.reminders: Dict[str, Dict[str, any]] = {}
        self.notification_log: List[Dict[str, str]] = []

    def add_reminder(self, reminder_id: str, event_name: str, event_time: str, notification_channel: str) -> None:
        """
        Add a calendar reminder.

        Args:
            reminder_id: Unique identifier for the reminder
            event_name: Name of the calendar event
            event_time: Time of the event (ISO format)
            notification_channel: Channel to send notification (e.g., 'slack', 'whatsapp', 'email')

        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(reminder_id, str) or not reminder_id.strip():
            raise ValueError("reminder_id must be a non-empty string")

        if not isinstance(event_name, str) or not event_name.strip():
            raise ValueError("event_name must be a non-empty string")

        if not isinstance(event_time, str) or not event_time.strip():
            raise ValueError("event_time must be a non-empty string")

        if not isinstance(notification_channel, str) or not notification_channel.strip():
            raise ValueError("notification_channel must be a non-empty string")

        self.reminders[reminder_id] = {
            'event_name': event_name,
            'event_time': event_time,
            'notification_channel': notification_channel,
            'created_at': datetime.now().isoformat(),
            'sent': False
        }

    def send_reminder(self, reminder_id: str) -> bool:
        """
        Send a reminder notification.

        Args:
            reminder_id: ID of the reminder to send

        Returns:
            True if reminder was sent, False if not found

        Raises:
            ValueError: If reminder_id is invalid
        """
        if not isinstance(reminder_id, str) or not reminder_id.strip():
            raise ValueError("reminder_id must be a non-empty string")

        if reminder_id not in self.reminders:
            return False

        reminder = self.reminders[reminder_id]
        
        # Log the notification
        self.notification_log.append({
            'reminder_id': reminder_id,
            'event_name': reminder['event_name'],
            'channel': reminder['notification_channel'],
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        })

        # Mark as sent
        reminder['sent'] = True

        return True

    def get_reminder(self, reminder_id: str) -> Optional[Dict[str, any]]:
        """
        Get a reminder by ID.

        Args:
            reminder_id: ID of the reminder

        Returns:
            Reminder dictionary if found, None otherwise
        """
        return self.reminders.get(reminder_id)

    def get_all_reminders(self) -> Dict[str, Dict[str, any]]:
        """
        Get all reminders.

        Returns:
            Dictionary of all reminders
        """
        return self.reminders.copy()

    def remove_reminder(self, reminder_id: str) -> bool:
        """
        Remove a reminder by ID.

        Args:
            reminder_id: ID of the reminder to remove

        Returns:
            True if reminder was removed, False if not found
        """
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            return True
        return False

    def get_notification_log(self) -> List[Dict[str, str]]:
        """
        Get the notification log.

        Returns:
            List of notification log entries
        """
        return self.notification_log.copy()

    def clear_reminders(self) -> None:
        """Clear all reminders."""
        self.reminders.clear()

    def clear_notification_log(self) -> None:
        """Clear the notification log."""
        self.notification_log.clear()

"""Tests for Communication Automation Module."""

import pytest
from hypothesis import given, strategies as st
from src.communication_automation import EmailSummarizer, TemplateResponder, NotificationBot
from src.data_models import EmailSummary


# EmailSummarizer Tests

def test_email_summarizer_basic_summarization():
    """Test basic email summarization."""
    email_body = "This is a long email. It contains multiple sentences. Each sentence provides information."
    summary = EmailSummarizer.summarize_email(email_body, max_length=50)
    
    assert isinstance(summary, str)
    assert len(summary) <= 50
    assert len(summary) < len(email_body)


def test_email_summarizer_short_email():
    """Test that short emails are not truncated."""
    email_body = "Short email."
    summary = EmailSummarizer.summarize_email(email_body, max_length=100)
    
    assert summary == email_body


def test_email_summarizer_empty_email():
    """Test that empty email raises error."""
    with pytest.raises(ValueError):
        EmailSummarizer.summarize_email("", max_length=100)


def test_email_summarizer_invalid_max_length():
    """Test that invalid max_length raises error."""
    with pytest.raises(ValueError):
        EmailSummarizer.summarize_email("test email", max_length=0)


def test_email_summarizer_create_summary():
    """Test creating an EmailSummary object."""
    summary = EmailSummarizer.create_email_summary(
        sender="test@example.com",
        subject="Test Subject",
        email_body="This is a test email body with multiple sentences.",
        max_summary_length=50
    )
    
    assert isinstance(summary, EmailSummary)
    assert summary.sender == "test@example.com"
    assert summary.subject == "Test Subject"
    assert summary.summary_length <= 50
    assert summary.original_length > 0


def test_email_summarizer_create_summary_invalid_sender():
    """Test that invalid sender raises error."""
    with pytest.raises(ValueError):
        EmailSummarizer.create_email_summary(
            sender="",
            subject="Test",
            email_body="Test body"
        )


def test_email_summarizer_batch_summarize():
    """Test batch summarization of multiple emails."""
    emails = [
        {
            'sender': 'user1@example.com',
            'subject': 'Subject 1',
            'body': 'This is the first email body with content.'
        },
        {
            'sender': 'user2@example.com',
            'subject': 'Subject 2',
            'body': 'This is the second email body with different content.'
        }
    ]
    
    summaries = EmailSummarizer.batch_summarize_emails(emails, max_summary_length=50)
    
    assert len(summaries) == 2
    assert all(isinstance(s, EmailSummary) for s in summaries)
    assert summaries[0].sender == 'user1@example.com'
    assert summaries[1].sender == 'user2@example.com'


def test_email_summarizer_batch_summarize_empty_list():
    """Test that empty email list raises error."""
    with pytest.raises(ValueError):
        EmailSummarizer.batch_summarize_emails([])


def test_email_summarizer_batch_summarize_invalid_email():
    """Test that invalid email format raises error."""
    emails = [
        {
            'sender': 'user@example.com',
            'subject': 'Subject',
            # Missing 'body' key
        }
    ]
    
    with pytest.raises(ValueError):
        EmailSummarizer.batch_summarize_emails(emails)


# TemplateResponder Tests

def test_template_responder_add_template():
    """Test adding a template."""
    responder = TemplateResponder()
    responder.add_template(
        template_id="template_1",
        keywords=["urgent", "asap"],
        response="This is urgent. I will handle it immediately."
    )
    
    templates = responder.get_all_templates()
    assert "template_1" in templates
    assert "urgent" in templates["template_1"]["keywords"]


def test_template_responder_add_template_invalid_id():
    """Test that invalid template_id raises error."""
    responder = TemplateResponder()
    
    with pytest.raises(ValueError):
        responder.add_template(
            template_id="",
            keywords=["test"],
            response="response"
        )


def test_template_responder_add_template_empty_keywords():
    """Test that empty keywords list raises error."""
    responder = TemplateResponder()
    
    with pytest.raises(ValueError):
        responder.add_template(
            template_id="template_1",
            keywords=[],
            response="response"
        )


def test_template_responder_find_matching_template():
    """Test finding a matching template."""
    responder = TemplateResponder()
    responder.add_template(
        template_id="template_1",
        keywords=["urgent", "asap"],
        response="This is urgent."
    )
    responder.add_template(
        template_id="template_2",
        keywords=["meeting", "schedule"],
        response="Let me check my calendar."
    )
    
    # Test matching first template
    match = responder.find_matching_template("This is urgent and needs immediate attention")
    assert match is not None
    assert match[0] == "template_1"
    assert match[1] == "This is urgent."
    
    # Test matching second template
    match = responder.find_matching_template("Can we schedule a meeting?")
    assert match is not None
    assert match[0] == "template_2"


def test_template_responder_find_matching_template_no_match():
    """Test when no template matches."""
    responder = TemplateResponder()
    responder.add_template(
        template_id="template_1",
        keywords=["urgent"],
        response="This is urgent."
    )
    
    match = responder.find_matching_template("This is a normal email")
    assert match is None


def test_template_responder_find_matching_template_case_insensitive():
    """Test that template matching is case-insensitive."""
    responder = TemplateResponder()
    responder.add_template(
        template_id="template_1",
        keywords=["URGENT"],
        response="This is urgent."
    )
    
    match = responder.find_matching_template("This is urgent and needs attention")
    assert match is not None


def test_template_responder_remove_template():
    """Test removing a template."""
    responder = TemplateResponder()
    responder.add_template(
        template_id="template_1",
        keywords=["test"],
        response="response"
    )
    
    assert responder.remove_template("template_1") is True
    assert "template_1" not in responder.get_all_templates()


def test_template_responder_remove_nonexistent_template():
    """Test removing a nonexistent template."""
    responder = TemplateResponder()
    assert responder.remove_template("nonexistent") is False


def test_template_responder_clear_templates():
    """Test clearing all templates."""
    responder = TemplateResponder()
    responder.add_template("template_1", ["test"], "response")
    responder.add_template("template_2", ["test2"], "response2")
    
    responder.clear_templates()
    assert len(responder.get_all_templates()) == 0


# NotificationBot Tests

def test_notification_bot_add_reminder():
    """Test adding a reminder."""
    bot = NotificationBot()
    bot.add_reminder(
        reminder_id="reminder_1",
        event_name="Team Meeting",
        event_time="2024-01-15T10:00:00",
        notification_channel="slack"
    )
    
    reminder = bot.get_reminder("reminder_1")
    assert reminder is not None
    assert reminder["event_name"] == "Team Meeting"
    assert reminder["notification_channel"] == "slack"


def test_notification_bot_add_reminder_invalid_id():
    """Test that invalid reminder_id raises error."""
    bot = NotificationBot()
    
    with pytest.raises(ValueError):
        bot.add_reminder(
            reminder_id="",
            event_name="Event",
            event_time="2024-01-15T10:00:00",
            notification_channel="slack"
        )


def test_notification_bot_add_reminder_invalid_event_name():
    """Test that invalid event_name raises error."""
    bot = NotificationBot()
    
    with pytest.raises(ValueError):
        bot.add_reminder(
            reminder_id="reminder_1",
            event_name="",
            event_time="2024-01-15T10:00:00",
            notification_channel="slack"
        )


def test_notification_bot_send_reminder():
    """Test sending a reminder."""
    bot = NotificationBot()
    bot.add_reminder(
        reminder_id="reminder_1",
        event_name="Team Meeting",
        event_time="2024-01-15T10:00:00",
        notification_channel="slack"
    )
    
    result = bot.send_reminder("reminder_1")
    assert result is True
    
    reminder = bot.get_reminder("reminder_1")
    assert reminder["sent"] is True


def test_notification_bot_send_nonexistent_reminder():
    """Test sending a nonexistent reminder."""
    bot = NotificationBot()
    result = bot.send_reminder("nonexistent")
    assert result is False


def test_notification_bot_notification_log():
    """Test notification logging."""
    bot = NotificationBot()
    bot.add_reminder(
        reminder_id="reminder_1",
        event_name="Team Meeting",
        event_time="2024-01-15T10:00:00",
        notification_channel="slack"
    )
    
    bot.send_reminder("reminder_1")
    
    log = bot.get_notification_log()
    assert len(log) == 1
    assert log[0]["reminder_id"] == "reminder_1"
    assert log[0]["status"] == "sent"


def test_notification_bot_remove_reminder():
    """Test removing a reminder."""
    bot = NotificationBot()
    bot.add_reminder(
        reminder_id="reminder_1",
        event_name="Event",
        event_time="2024-01-15T10:00:00",
        notification_channel="slack"
    )
    
    assert bot.remove_reminder("reminder_1") is True
    assert bot.get_reminder("reminder_1") is None


def test_notification_bot_remove_nonexistent_reminder():
    """Test removing a nonexistent reminder."""
    bot = NotificationBot()
    assert bot.remove_reminder("nonexistent") is False


def test_notification_bot_clear_reminders():
    """Test clearing all reminders."""
    bot = NotificationBot()
    bot.add_reminder("reminder_1", "Event 1", "2024-01-15T10:00:00", "slack")
    bot.add_reminder("reminder_2", "Event 2", "2024-01-16T10:00:00", "email")
    
    bot.clear_reminders()
    assert len(bot.get_all_reminders()) == 0


def test_notification_bot_clear_notification_log():
    """Test clearing notification log."""
    bot = NotificationBot()
    bot.add_reminder("reminder_1", "Event", "2024-01-15T10:00:00", "slack")
    bot.send_reminder("reminder_1")
    
    bot.clear_notification_log()
    assert len(bot.get_notification_log()) == 0


# Property-Based Tests

@given(
    email_body=st.text(min_size=1, max_size=500),
    max_length=st.integers(min_value=1, max_value=200)
)
def test_email_summary_reduction(email_body, max_length):
    """
    **Feature: lazy-automation-platform, Property 6: Email Summary Reduction**
    
    For any email text, the generated summary should be shorter than or equal to 
    the original email content.
    
    **Validates: Requirements 2.2**
    """
    # Skip if email_body is only whitespace
    if not email_body.strip():
        return
    
    summary = EmailSummarizer.summarize_email(email_body, max_length=max_length)
    
    # Summary should be a string
    assert isinstance(summary, str), f"Summary should be string, got {type(summary)}"
    
    # Summary should not exceed max_length
    assert len(summary) <= max_length, \
        f"Summary length {len(summary)} exceeds max_length {max_length}"
    
    # Summary should be shorter than or equal to original
    assert len(summary) <= len(email_body), \
        f"Summary length {len(summary)} should be <= original length {len(email_body)}"


@given(
    email_text=st.text(min_size=1, max_size=200),
    keyword=st.text(min_size=1, max_size=20)
)
def test_template_matching_consistency(email_text, keyword):
    """
    **Feature: lazy-automation-platform, Property 7: Template Matching Consistency**
    
    For any set of templates and incoming email text, the template matching algorithm 
    should consistently return the same template for identical inputs.
    
    **Validates: Requirements 2.3, 2.4**
    """
    # Skip if inputs are only whitespace
    if not email_text.strip() or not keyword.strip():
        return
    
    responder = TemplateResponder()
    responder.add_template(
        template_id="template_1",
        keywords=[keyword],
        response="Test response"
    )
    
    # Test consistency: calling find_matching_template twice should return same result
    match1 = responder.find_matching_template(email_text)
    match2 = responder.find_matching_template(email_text)
    
    # Both calls should return the same result
    assert match1 == match2, \
        f"Template matching should be consistent: {match1} != {match2}"
    
    # If keyword is in email_text (case-insensitive), should match
    if keyword.lower() in email_text.lower():
        assert match1 is not None, \
            f"Should find match when keyword '{keyword}' is in email text"
        assert match1[0] == "template_1", \
            f"Should return correct template_id"
        assert match1[1] == "Test response", \
            f"Should return correct response"

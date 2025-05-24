import pytest
from unittest.mock import MagicMock, patch
from utils.email_checker import EmailChecker, ParsedEmail


@pytest.fixture
def dummy_email():
    """
    Fixture that returns a dummy ParsedEmail object with a subject, body, and attachment.
    """
    return ParsedEmail(
        subject="Test Subject",
        body="Hello world!\nThis is a test email.\nLink: https://example.com",
        attachments=["cv.pdf"]
    )


@pytest.fixture
def email_checker():
    """
    Fixture that returns a configured EmailChecker instance for testing.
    """
    return EmailChecker(
        server="imap.example.com",
        port=993,
        username="test@example.com",
        password="secret",
        use_ssl=True
    )


def test_parse_email_text_only(email_checker):
    """
    Should correctly parse a plain text email with a subject and body.
    """
    raw_email = b"Subject: Hello\r\n\r\nThis is the body."
    parsed = email_checker._parse_email(raw_email)
    assert "hello" in parsed.subject.lower()
    assert "body" in parsed.body.lower()


def test_check_email_content_passes(email_checker, dummy_email):
    """
    Should pass validation when the expected body content and attachment match.
    """
    email_checker._last_email = dummy_email
    email_checker._last_uid = b"1"
    email_checker.connection = MagicMock()
    email_checker.wait_for_email = MagicMock(return_value=True)
    email_checker.get_email_by_subject_contains = MagicMock(return_value=dummy_email)

    config_section = {
        "subject_contains": "Test Subject",
        "must_contain": ["Hello world!", "Link:"],
        "check_form_fields": ["portfolio", "resume"],
        "timeout_seconds": 5,
    }

    form_fields = [
        {"name": "portfolio", "type": "text", "required": True, "value": "https://example.com"},
        {"name": "resume", "type": "file", "required": True, "file": "cv.pdf"},
    ]

    email_checker.check_email_content(config_section, form_fields)


def test_check_email_content_fails_on_missing_text(email_checker, dummy_email):
    """
    Should raise an AssertionError if the expected body content is missing.
    """
    email_checker._last_email = dummy_email
    email_checker._last_uid = b"1"
    email_checker.connection = MagicMock()
    email_checker.wait_for_email = MagicMock(return_value=True)
    email_checker.get_email_by_subject_contains = MagicMock(return_value=dummy_email)

    config_section = {
        "subject_contains": "Test Subject",
        "must_contain": ["This text is missing"],
        "check_form_fields": [],
        "timeout_seconds": 5,
    }

    with pytest.raises(AssertionError):
        email_checker.check_email_content(config_section, [])


@pytest.mark.parametrize("use_ssl", [True, False])
def test_connect_establishes_connection(use_ssl):
    """
    Should connect to the IMAP server and perform login using the correct protocol.
    """
    imap_class = "imaplib.IMAP4_SSL" if use_ssl else "imaplib.IMAP4"
    with patch(imap_class) as mock_imap:
        instance = mock_imap.return_value
        instance.login.return_value = "OK"
        checker = EmailChecker("imap.example.com", 993, "user", "pass", use_ssl=use_ssl)
        conn = checker._connect()
        assert conn.login.called
        assert checker.connection == conn
import imaplib
import email
from email.header import decode_header
from email.message import Message
import time
from typing import Optional, List, Union




class ParsedEmail:
    """
    Represents a parsed email with its subject, body, and attachments.
    """

    def __init__(self, subject: str, body: str, attachments: List[str]):
        self.subject = subject
        self.body = body
        self.attachments = attachments


class EmailChecker:
    """
    A utility class for connecting to an IMAP inbox and verifying email content.

    Supports:
    - Connecting via IMAP/IMAP-SSL
    - Polling for an incoming email matching given criteria
    - Parsing subject, body, and attachments
    - Verifying email content against config
    - Deleting processed messages
    """

    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool = True
    ):
        """
        Initializes the email checker with IMAP connection details.

        Args:
            server: IMAP server hostname.
            port: IMAP server port (e.g. 993 for SSL).
            username: Email address used for login.
            password: Corresponding password or app password.
            use_ssl: Whether to use SSL connection. Default is True.
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection: Optional[imaplib.IMAP4] = None
        self._last_uid: Optional[bytes] = None
        self._last_email: Optional[ParsedEmail] = None

    def _connect(self) -> Union[imaplib.IMAP4, imaplib.IMAP4_SSL]:
        """
        Establishes and stores a connection to the IMAP server.

        Returns:
            The IMAP connection object.
        """
        if self.connection is None:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            self.connection.login(self.username, self.password)
        return self.connection

    def _parse_email(self, raw_email: bytes) -> ParsedEmail:
        """
        Parses a raw email message into subject, body, and attachment list.

        Args:
            raw_email: Raw email message as bytes.

        Returns:
            ParsedEmail: A parsed email object.
        """
        msg: Message = email.message_from_bytes(raw_email)
        subject_raw = msg.get("Subject", "")
        subject, encoding = decode_header(subject_raw)[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="replace")

        body = ""
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", "")).lower()
                content_type = part.get_content_type()

                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
                elif content_type == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body += payload.decode(charset, errors="replace")
                    except Exception:
                        continue
        else:
            charset = msg.get_content_charset() or "utf-8"
            try:
                payload = msg.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode(charset, errors="replace")
            except Exception:
                body = ""

        return ParsedEmail(subject=subject, body=body, attachments=attachments)

    def wait_for_email(self, subject_contains: Optional[str] = None,
                       must_contain: Optional[List[str]] = None,
                       timeout_seconds: int = 60) -> bool:
        """
        Waits for an incoming email that matches the given criteria.

        Args:
            subject_contains: Text that must appear in the email subject.
            must_contain: List of strings that must appear in the email body.
            timeout_seconds: How long to wait for a matching email.

        Returns:
            True if a matching email is found; False if timeout is reached.
        """
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            self._connect()
            assert self.connection is not None
            self.connection.select("INBOX")
            typ, data = self.connection.search(None, "ALL")
            if typ != "OK":
                continue

            for num in reversed(data[0].split()):
                typ, msg_data = self.connection.fetch(num, "(RFC822)")
                if typ != "OK":
                    continue
                part = msg_data[0]
                if isinstance(part, tuple) and len(part) > 1 and isinstance(part[1], bytes):
                    raw_email = part[1]
                else:
                    continue

                parsed = self._parse_email(raw_email)

                subject_ok = (
                    subject_contains is None
                    or subject_contains.lower() in parsed.subject.lower()
                )
                content_ok = all(
                    text.lower() in parsed.body.lower() for text in must_contain or []
                )

                if subject_ok and content_ok:
                    self._last_email = parsed
                    self._last_uid = num
                    return True
            time.sleep(2)
        return False

    def get_email_by_subject_contains(self, subject_fragment: str) -> ParsedEmail:
        """
        Finds and returns the latest email whose subject contains the given fragment.

        Args:
            subject_fragment: Text fragment expected in subject.

        Returns:
            ParsedEmail object of the matching email.

        Raises:
            ValueError: If no matching email is found.
        """
        self._connect()
        assert self.connection is not None
        self.connection.select("INBOX")
        typ, data = self.connection.search(None, "ALL")
        if typ != "OK":
            raise RuntimeError("Cannot search mailbox")

        for num in reversed(data[0].split()):
            typ, msg_data = self.connection.fetch(num, "(RFC822)")
            if typ != "OK":
                continue
            part = msg_data[0]
            if isinstance(part, tuple) and len(part) > 1:
                raw_email = part[1]
            else:
                continue

            parsed = self._parse_email(raw_email)
            if subject_fragment.lower() in parsed.subject.lower():
                self._last_uid = num
                return parsed

        raise ValueError(f"No email found with subject containing: {subject_fragment}")

    def check_email_content(self, config_section: dict, form_fields: list) -> None:
        """
        Waits for an email and validates its content based on configuration.

        Args:
            config_section: A dictionary with keys:
                - subject_contains
                - must_contain
                - check_form_fields
                - timeout_seconds
            form_fields: The original list of form fields to compare values/attachments.

        Raises:
            AssertionError: If required text or attachments are missing.
        """
        time.sleep(2)
        subject_part = config_section["subject_contains"]
        timeout = config_section.get("timeout_seconds", 60)

        assert self.wait_for_email(subject_contains=subject_part, timeout_seconds=timeout), (
            f"Email with subject containing '{subject_part}' not received"
        )

        email = self.get_email_by_subject_contains(subject_part)
        body = email.body.lower()
        attachments = email.attachments or []

        for item in config_section.get("must_contain", []):
            assert item.lower() in body, f"Expected '{item}' in email body"

        for field_name in config_section.get("check_form_fields", []):
            field = next((f for f in form_fields if f["name"] == field_name), None)
            assert field, f"Field '{field_name}' not found in form_fields"

            if not field.get("required", False):
                continue

            field_type = field.get("type", "text")

            if field_type == "file":
                if "file" in field:
                    assert attachments, f"Expected file attachment for '{field_name}'"
            else:
                expected = field.get("value", "").strip().lower()
                if expected:
                    assert expected in body, f"Expected value '{expected}' for field '{field_name}' not found in email body"

        if self.connection and self._last_uid:
            self.connection.store(self._last_uid.decode(), "+FLAGS", r"(\Deleted)")
            self.connection.expunge()

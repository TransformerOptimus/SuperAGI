import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from config.config import config
from datetime import datetime, timedelta


class ReadEmailSchema(BaseModel):
    """Schema for reading emails"""
    max_emails: int = Field(
        default=10,
        description="Maximum number of emails to retrieve"
    )
    unread_only: bool = Field(
        default=True,
        description="Whether to only fetch unread emails"
    )
    since_days: int = Field(
        default=7,
        description="Only fetch emails from the last N days"
    )


class ReadEmailTool(BaseTool):
    """
    Email Reading Tool for monitoring responses

    Reads emails from inbox to track prospect responses and replies
    to outreach campaigns.
    """

    name = "read_email"
    description = (
        "Read emails from inbox to check for prospect responses. "
        "Use this to monitor replies to outreach emails and track engagement."
    )
    args_schema = ReadEmailSchema

    def execute(
        self,
        max_emails: int = 10,
        unread_only: bool = True,
        since_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Read emails from inbox

        Args:
            max_emails: Maximum number of emails to retrieve
            unread_only: Only fetch unread emails
            since_days: Only fetch emails from last N days

        Returns:
            List of email dictionaries
        """
        if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
            return [{
                "error": "Email credentials not configured"
            }]

        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(config.EMAIL_IMAP_SERVER)
            mail.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            mail.select("inbox")

            # Build search criteria
            since_date = (datetime.now() - timedelta(days=since_days)).strftime("%d-%b-%Y")

            if unread_only:
                search_criteria = f'(UNSEEN SINCE {since_date})'
            else:
                search_criteria = f'(SINCE {since_date})'

            # Search for emails
            status, messages = mail.search(None, search_criteria)

            if status != "OK":
                return []

            email_ids = messages[0].split()
            email_list = []

            # Fetch emails (most recent first)
            for email_id in reversed(email_ids[:max_emails]):
                status, msg_data = mail.fetch(email_id, "(RFC822)")

                if status != "OK":
                    continue

                # Parse email
                msg = email.message_from_bytes(msg_data[0][1])

                # Decode subject
                subject = self._decode_header(msg.get("Subject", ""))
                from_addr = self._decode_header(msg.get("From", ""))
                date = msg.get("Date", "")

                # Get email body
                body = self._get_email_body(msg)

                email_list.append({
                    "from": from_addr,
                    "subject": subject,
                    "date": date,
                    "body": body[:500],  # First 500 chars
                    "is_unread": unread_only
                })

            mail.close()
            mail.logout()

            return email_list

        except imaplib.IMAP4.error as e:
            return [{
                "error": f"IMAP error: {str(e)}"
            }]
        except Exception as e:
            return [{
                "error": f"Failed to read emails: {str(e)}"
            }]

    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""

        decoded = decode_header(header)
        result = ""

        for part, encoding in decoded:
            if isinstance(part, bytes):
                result += part.decode(encoding or "utf-8", errors="ignore")
            else:
                result += part

        return result

    def _get_email_body(self, msg) -> str:
        """Extract email body from message"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except:
                        continue
        else:
            try:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                body = ""

        return body

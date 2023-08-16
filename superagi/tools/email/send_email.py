import imaplib
import smtplib
import time
from email.message import EmailMessage
from typing import Type

from pydantic import BaseModel, Field
from superagi.helper.imap_email import ImapEmail
from superagi.tools.base_tool import BaseTool


class SendEmailInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default email address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent. Escape special characters in the body. Do not add senders details and end it with Warm Regards without entering any name.")


class SendEmailTool(BaseTool):
    """
    Send an Email tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Send Email"
    args_schema: Type[BaseModel] = SendEmailInput
    description: str = "Send an Email"
    
    def _execute(self, to: str, subject: str, body: str) -> str:
        """
        Execute the send email tool.

        Args:
            to : The email address of the receiver.
            subject : The subject of the email.
            body : The body of the email.

        Returns:
            success or error message.
        """
        email_sender = self.get_tool_config('EMAIL_ADDRESS')
        email_password = self.get_tool_config('EMAIL_PASSWORD')
        if email_sender is None or email_sender == "" or email_sender.isspace():
            return "Error: Email Not Sent. Enter a valid Email Address."
        if email_password is None or email_password == "" or email_password.isspace():
            return "Error: Email Not Sent. Enter a valid Email Password."
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = email_sender
        message["To"] = to
        signature = self.get_tool_config('EMAIL_SIGNATURE')
        if signature:
            body += f"\n{signature}"
        message.set_content(body)

        send_to_draft = self.get_tool_config('EMAIL_DRAFT_MODE') or "FALSE"
        if send_to_draft.upper() == "TRUE":
            send_to_draft = True
        else:
            send_to_draft = False

        if message["To"] == "example@example.com" or send_to_draft:
            draft_folder = self.get_tool_config('EMAIL_DRAFT_FOLDER') or "Drafts"
            imap_server = self.get_tool_config('EMAIL_IMAP_SERVER')
            conn = ImapEmail().imap_open(draft_folder, email_sender, email_password, imap_server)
            conn.append(
                draft_folder,
                "",
                imaplib.Time2Internaldate(time.time()),
                str(message).encode("UTF-8")
            )
            return f"Email went to {draft_folder}"
        else:
            smtp_host = self.get_tool_config('EMAIL_SMTP_HOST')
            smtp_port = self.get_tool_config('EMAIL_SMTP_PORT')
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(email_sender, email_password)
                smtp.send_message(message)
                smtp.quit()
            return f"Email was sent to {to}"

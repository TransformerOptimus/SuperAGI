import imaplib
import mimetypes
import os
import smtplib
import time
from email.message import EmailMessage
from typing import Type

from pydantic import BaseModel, Field

from superagi.config.config import get_config
from superagi.helper.imap_email import ImapEmail
from superagi.tools.base_tool import BaseTool


class SendEmailAttachmentInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default email address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent")
    filename: str = Field(..., description="Name of the file to be sent as an Attachement with Email")


class SendEmailAttachmentTool(BaseTool):
    name: str = "Helps Send Email with Attachement"
    args_schema: Type[BaseModel] = SendEmailAttachmentInput
    description: str = "Send an Email with a file attached to it"

    def _execute(self, to: str, subject: str, body: str, filename: str) -> str:
        base_path = get_config('EMAIL_ATTACHMENT_BASE_PATH')
        if not base_path:
            base_path = ""
        base_path = base_path + filename
        attachmentpath = base_path
        attachment = os.path.basename(attachmentpath)
        return self.send_email_with_attachement(to, subject, body, attachmentpath, attachment)

    def send_email_with_attachement(self, to, subject, body, attachment_path, attachment) -> str:
        email_sender = get_config('EMAIL_ADDRESS')
        email_password = get_config('EMAIL_PASSWORD')
        if email_sender == "" or email_sender.isspace():
            return "Error: Email Not Sent. Enter a valid Email Address."
        if email_password == "" or email_password.isspace():
            return "Error: Email Not Sent. Enter a valid Email Password."
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = email_sender
        message["To"] = to
        signature = get_config('EMAIL_SIGNATURE')
        if signature:
            body += f"\n{signature}"
        message.set_content(body)
        if attachment_path:
            ctype, encoding = mimetypes.guess_type(attachment_path)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            with open(attachment_path, "rb") as file:
                message.add_attachment(file.read(), maintype=maintype, subtype=subtype, filename=attachment)
        draft_folder = get_config('EMAIL_DRAFT_MODE_WITH_FOLDER')
        
        if message["To"] == "example@example.com" or draft_folder:
            conn = ImapEmail().imap_open(draft_folder, email_sender, email_password)
            conn.append(
                draft_folder,
                "",
                imaplib.Time2Internaldate(time.time()),
                str(message).encode("UTF-8")
            )
            return f"Email went to {draft_folder}"
        else:
            smtp_host = get_config('EMAIL_SMTP_HOST')
            smtp_port = get_config('EMAIL_SMTP_PORT')
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(email_sender, email_password)
                smtp.send_message(message)
                smtp.quit()
            return f"Email was sent to {to}"

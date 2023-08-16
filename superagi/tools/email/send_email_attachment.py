import imaplib
import mimetypes
import os
import smtplib
import time
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Type

from pydantic import BaseModel, Field

from superagi.config.config import get_config
from superagi.helper.imap_email import ImapEmail
from superagi.helper.resource_helper import ResourceHelper
from superagi.helper.s3_helper import S3Helper
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.types.storage_types import StorageType


class SendEmailAttachmentInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default email address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent, Do not add senders details in the email body and end it with Warm Regards without entering any name.")
    filename: str = Field(..., description="Name of the file to be sent as an Attachment with Email")


class SendEmailAttachmentTool(BaseTool):
    """
    Send an Email with Attachment tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Send Email with Attachment"
    args_schema: Type[BaseModel] = SendEmailAttachmentInput
    description: str = "Send an Email with a file attached to it"
    agent_id: int = None
    agent_execution_id: int = None

    def _execute(self, to: str, subject: str, body: str, filename: str) -> str:
        """
        Execute the send email tool with attachment.

        Args:
            to : The email address of the receiver.
            subject : The subject of the email.
            body : The body of the email.
            filename : The name of the file to be sent as an attachment with the email.

        Returns:
            success or failure message
        """
        final_path = ResourceHelper.get_agent_read_resource_path(file_name=filename,
                                                                 agent=Agent.get_agent_from_id(
                                                                     self.toolkit_config.session,
                                                                     self.agent_id),
                                                                 agent_execution=AgentExecution.get_agent_execution_from_id(
                                                                     session=self.toolkit_config.session,
                                                                     agent_execution_id=self.agent_execution_id)
                                                                 )
        ctype, encoding = mimetypes.guess_type(final_path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        if StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value)) == StorageType.S3:
            attachment_data = S3Helper().read_binary_from_s3(final_path)
        else:
            if final_path is None or not os.path.exists(final_path):
                raise FileNotFoundError(f"File '{filename}' not found.")
            with open(final_path, "rb") as file:
                attachment_data = file.read()
        attachment = MIMEApplication(attachment_data)
        attachment.add_header('Content-Disposition', 'attachment', filename=final_path.split('/')[-1])

        return self.send_email_with_attachment(to, subject, body, attachment)

    def send_email_with_attachment(self, to, subject, body, attachment) -> str:
        """
        Send an email with attachment.

        Args:
            to : The email address of the receiver.
            subject : The subject of the email.
            body : The body of the email.
            attachment : The data of the file to be sent as an attachment with the email.

        Returns:
            
        """
        email_sender = self.get_tool_config('EMAIL_ADDRESS')
        email_password = self.get_tool_config('EMAIL_PASSWORD')
        if email_sender is None or email_sender == "" or email_sender.isspace():
            return "Error: Email Not Sent. Enter a valid Email Address."
        if email_password is None or email_password == "" or email_password.isspace():
            return "Error: Email Not Sent. Enter a valid Email Password."
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = email_sender
        message["To"] = to
        signature = self.get_tool_config('EMAIL_SIGNATURE')
        if signature:
            body += f"\n{signature}"
        message.attach(MIMEText(body, 'plain'))
        if attachment:
            message.attach(attachment)

        send_to_draft = self.get_tool_config('EMAIL_DRAFT_MODE') or "FALSE"
        if send_to_draft.upper() == "TRUE":
            send_to_draft = True
        else:
            send_to_draft = False
        if message["To"] == "example@example.com" or send_to_draft:
            draft_folder = self.get_tool_config('EMAIL_DRAFT_FOLDER')
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

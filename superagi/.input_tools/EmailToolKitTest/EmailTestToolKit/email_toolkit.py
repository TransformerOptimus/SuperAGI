from abc import ABC
from superagi_tools_lib import BaseToolKit, BaseTool
from typing import Type, List
from read_email import ReadEmailTool
from send_email import SendEmailTool
from send_email_attachment import SendEmailAttachmentTool

from pydantic import BaseModel, Field


class EmailToolKit(BaseToolKit, ABC):
    name: str = "Test Email Toolkit"
    description: str = "This is a test email toolkit"

    def get_tools(self) -> List[BaseTool]:
        return [ReadEmailTool(), SendEmailTool(),SendEmailAttachmentTool()]

    def get_env_keys(self) -> List[str]:
        return ["EMAIL_ADDRESS", "EMAIL_PASSWORD", "EMAIL_SIGNATURE", "EMAIL_DRAFT_MODE_WITH_FOLDER", "EMAIL_SMTP_HOST", "EMAIL_SMTP_PORT","EMAIL_ATTACHMENT_BASE_PATH","EMAIL_IMAP_SERVER"]
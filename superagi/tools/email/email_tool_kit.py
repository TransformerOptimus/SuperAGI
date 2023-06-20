from abc import ABC
from superagi.tools.base_tool import BaseToolKit, BaseTool
from typing import Type, List
from read_email import ReadEmailTool
from send_email import SendEmailTool
from send_email_attachment import SendEmailAttachmentTool


class EmailToolKit(BaseToolKit, ABC):
    name: str = "Email Toolkit"
    description: str = "Email Tool kit contains all tools related to sending email"

    def get_tools(self) -> List[BaseTool]:
        return [ReadEmailTool(), SendEmailTool(),SendEmailAttachmentTool()]


    def get_env_keys(self) -> List[str]:
        return ["EMAIL_ADDRESS", "EMAIL_PASSWORD", "EMAIL_SIGNATURE", "EMAIL_DRAFT_MODE", "EMAIL_DRAFT_FOLDER", "EMAIL_SMTP_HOST", "EMAIL_SMTP_PORT","EMAIL_IMAP_SERVER"]
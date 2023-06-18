from typing import Type

from pydantic import BaseModel, Field

from superagi_tools_lib import BaseTool


class SendEmailAttachmentInput(BaseModel):
    to: str = Field(..., description="Email Address of the Receiver, default EmailTestToolKit address is 'example@example.com'")
    subject: str = Field(..., description="Subject of the Email to be sent")
    body: str = Field(..., description="Email Body to be sent")
    filename: str = Field(..., description="Name of the file to be sent as an Attachement with Email")


class SendEmailAttachmentTool(BaseTool):
    name: str = "Helps Send Email with Attachement"
    args_schema: Type[BaseModel] = SendEmailAttachmentInput
    description: str = "Send an Email with a file attached to it"

    def _execute(self, to: str, subject: str, body: str, filename: str) -> str:
        return "Email Sent With Attachment!"

from typing import Type

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool


class ReadEmailInput(BaseModel):
    imap_folder: str = Field(..., description="Email folder to read from. default value is \"INBOX\"")
    page: int = Field(..., description="The index of the page result the function should resturn. Defaults to 0, the first page.")
    limit: int = Field(..., description="Number of emails to fetch in one cycle. Defaults to 5.")


class ReadEmailTool(BaseTool):
    name: str = "Read Email"
    args_schema: Type[BaseModel] = ReadEmailInput
    description: str = "Read emails from an IMAP mailbox"

    def _execute(self, imap_folder: str = "INBOX", page: int = 0, limit: int = 5) -> str:
            messages = "TESTING EMAIL"
            return messages

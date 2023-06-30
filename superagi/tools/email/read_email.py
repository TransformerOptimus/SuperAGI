import email
import json
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.imap_email import ImapEmail
from superagi.helper.read_email import ReadEmail
from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool


class ReadEmailInput(BaseModel):
    imap_folder: str = Field(..., description="Email folder to read from. default value is \"INBOX\"")
    page: int = Field(...,
                      description="The index of the page result the function should resturn. Defaults to 0, the first page.")
    limit: int = Field(..., description="Number of emails to fetch in one cycle. Defaults to 5.")


class ReadEmailTool(BaseTool):
    """
    Read emails from an IMAP mailbox

    Attributes:
        name : The name of the tool.
        description : The description of the tool.
        args_schema : The args schema.
    """
    name: str = "Read Email"
    args_schema: Type[BaseModel] = ReadEmailInput
    description: str = "Read emails from an IMAP mailbox"

    def _execute(self, imap_folder: str = "INBOX", page: int = 0, limit: int = 5) -> str:
        """
        Execute the read email tool.

        Args:
            imap_folder : The email folder to read from. Defaults to "INBOX".
            page : The index of the page result the function should return. Defaults to 0, the first page.
            limit : Number of emails to fetch in one cycle. Defaults to 5.

        Returns:
            email contents or error message.
        """
        email_sender = self.get_tool_config('EMAIL_ADDRESS')
        email_password = self.get_tool_config('EMAIL_PASSWORD')
        if email_sender == "":
            return "Error: Email Not Sent. Enter a valid Email Address."
        if email_password == "":
            return "Error: Email Not Sent. Enter a valid Email Password."
        imap_server = self.get_tool_config('EMAIL_IMAP_SERVER')
        conn = ImapEmail().imap_open(imap_folder, email_sender, email_password, imap_server)
        status, messages = conn.select("INBOX")
        num_of_messages = int(messages[0])
        messages = []
        for i in range(num_of_messages, num_of_messages - limit, -1):
            res, msg = conn.fetch(str(i), "(RFC822)")
            email_msg = {}
            for response in msg:
                self._process_message(email_msg, response)
            messages.append(email_msg)
            if TokenCounter.count_text_tokens(json.dumps(messages)) > self.max_token_limit:
                break

        conn.logout()
        if not messages:
            return f"There are no Email in your folder {imap_folder}"
        else:
            return messages

    def _process_message(self, email_msg, response):
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
            email_msg["From"], email_msg["To"], email_msg["Date"], email_msg[
                "Subject"] = ReadEmail().obtain_header(msg)
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        email_msg["Message Body"] = ReadEmail().clean_email_body(body)
                    elif "attachment" in content_disposition:
                        ReadEmail().download_attachment(part, email_msg["Subject"])
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    email_msg["Message Body"] = ReadEmail().clean_email_body(body)

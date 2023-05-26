from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.helper.imap_email import ImapEmail
from superagi.helper.read_email import ReadEmail
import email
import json
from email.header import decode_header

class ReadEmailTool(BaseTool):
    name: str = "Read Email"
    description: str = "Read an Email"
    
    def _execute(self,imap_folder: str = "INBOX", limit: int = 10) -> str:
        email_sender = get_config('EMAIL_ADDRESS')
        email_password = get_config('EMAIL_PASSWORD')
        if email_sender == "":
            return "Error: Email Not Sent. Enter a valid Email Address."
        if email_password == "":
            return "Error: Email Not Sent. Enter a valid Email Password."
        conn = ImapEmail().imap_open(imap_folder, email_sender, email_password)
        status, messages = conn.select("INBOX")
        num_of_messages = int(messages[0])
        messages = []
        for i in range(num_of_messages, num_of_messages - limit, -1):
            res, msg = conn.fetch(str(i), "(RFC822)")
            email_msg = {}
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    email_msg["From"], email_msg["To"],email_msg["Date"],email_msg["Subject"] = ReadEmail().obtain_header(msg)
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
            messages.append(email_msg)
        conn.logout()
        if not messages:
            return f"There are no Email in your folder {imap_folder}"
        else:
            return messages
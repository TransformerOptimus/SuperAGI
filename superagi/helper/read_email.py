import os
import re
from email.header import decode_header

from bs4 import BeautifulSoup


class ReadEmail:
    def clean_email_body(self, email_body):
        """
        Function to clean the email body.

        Args:
            email_body (str): The email body to be cleaned.

        Returns:
            str: The cleaned email body.
        """
        if email_body is None: email_body = ""
        email_body = BeautifulSoup(email_body, "html.parser")
        email_body = email_body.get_text()
        email_body = "".join(email_body.splitlines())
        email_body = " ".join(email_body.split())
        email_body = email_body.encode("ascii", "ignore")
        email_body = email_body.decode("utf-8", "ignore")
        email_body = re.sub(r"http\S+", "", email_body)
        return email_body

    def clean(self, text):
        """
        Function to clean the text.

        Args:
            text (str): The text to be cleaned.

        Returns:
            str: The cleaned text.
        """
        return "".join(c if c.isalnum() else "_" for c in text)

    def obtain_header(self, msg):
        """
        Function to obtain the header of the email.

        Args:
            msg (email.message.Message): The email message.

        Returns:
            str: The From field of the email.
        """
        if msg["Subject"] is not None:
            Subject, encoding = decode_header(msg["Subject"])[0]
        else:
            Subject = ""
            encoding = ""
        if isinstance(Subject, bytes):
            try:
                if encoding is not None:
                    Subject = Subject.decode(encoding)
                else:
                    Subject = ""
            except[LookupError] as err:
                pass
        From = msg["From"]
        To = msg["To"]
        Date = msg["Date"]
        return From, To, Date, Subject

    def download_attachment(self, part, subject):
        """
        Function to download the attachment from the email.

        Args:
            part (email.message.Message): The email message.
            subject (str): The subject of the email.

        Returns:
            None
        """
        filename = part.get_filename()
        if filename:
            folder_name = self.clean(subject)
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
                filepath = os.path.join(folder_name, filename)
                open(filepath, "wb").write(part.get_payload(decode=True))

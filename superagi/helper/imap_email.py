import imaplib
from superagi.config.config import get_config


class ImapEmail:

    def imap_open(self, imap_folder, email_sender, email_password) -> imaplib.IMAP4_SSL:
        imap_server = get_config('EMAIL_IMAP_SERVER')
        conn = imaplib.IMAP4_SSL(imap_server)
        conn.login(email_sender, email_password)
        conn.select(imap_folder)
        return conn

    def adjust_imap_folder(self, imap_folder, email_sender) -> str:
        if "@gmail" in email_sender.lower():
            if "sent" in imap_folder.lower():
                return '"[Gmail]/Sent Mail"'
            if "draft" in imap_folder.lower():
                return '"[Gmail]/Drafts"'
        return imap_folder

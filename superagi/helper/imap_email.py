import imaplib


class ImapEmail:

    def imap_open(self, imap_folder, email_sender, email_password, imap_server) -> imaplib.IMAP4_SSL:
        """
        Function to open an IMAP connection to the email server.

        Args:
            imap_folder (str): The folder to open.
            email_sender (str): The email address of the sender.
            email_password (str): The password of the sender.

        Returns:
            imaplib.IMAP4_SSL: The IMAP connection.
        """
        conn = imaplib.IMAP4_SSL(imap_server)
        conn.login(email_sender, email_password)
        conn.select(imap_folder)
        return conn

    def adjust_imap_folder(self, imap_folder, email_sender) -> str:
        """
        Function to adjust the IMAP folder based on the email address of the sender.

        Args:
            imap_folder (str): The folder to open.
            email_sender (str): The email address of the sender.

        Returns:
            str: The adjusted IMAP folder.
        """
        if "@gmail" in email_sender.lower():
            if "sent" in imap_folder.lower():
                return '"[Gmail]/Sent Mail"'
            if "draft" in imap_folder.lower():
                return '"[Gmail]/Drafts"'
        return imap_folder

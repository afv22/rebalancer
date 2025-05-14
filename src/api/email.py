import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.api.secret import GoogleSecretWrapper


class EmailClientWrapper:
    @classmethod
    def send(cls, subject: str, body: str):
        """
        Sends an email using Gmail's SMTP server.

        Args:
            subject (str): The subject of the email.
            body (str): The HTML content of the email body.

        """
        sender = recipient = os.getenv("GMAIL_ACCOUNT")
        password = GoogleSecretWrapper.get_secret("GmailAppPassword")

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

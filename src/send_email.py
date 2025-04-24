import dotenv
import smtplib
from email.mime.text import MIMEText


def send_email(subject, body):
    sender = "andrew.vagliano1@gmail.com"
    recipient = "andrew.vagliano1@gmail.com"
    password = dotenv.get_key("GMAIL_APP_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

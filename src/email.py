import os
import base64

from typing import Union
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

from src.gmail import gmail_resource


def _create_text_message(subject: str, html: str, recipient: str):
    load_dotenv()

    message = MIMEText(html, "html")
    message["to"] = recipient
    message["from"] = os.getenv("FROM_EMAIL")
    message["subject"] = subject

    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


def _send_message(service, message_object: dict):
    try:
        message = (
            service.users().messages().send(userId="me", body=message_object).execute()
        )
        print("Message Id: %s" % message["id"])
        return message
    except Exception as e:
        print("An error occurred: %s" % e)
        return None


def send_text_email(subject: str, html: str, recipient: str):
    service = gmail_resource()
    message_object = _create_text_message(subject, html, recipient)
    return _send_message(service, message_object)


def send_custom_email(message: Union[MIMEMultipart, MIMEText, MIMEImage]):
    service = gmail_resource()
    message_object = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
    return _send_message(service, message_object)

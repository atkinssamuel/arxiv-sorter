import os
import base64

from typing import Union
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from typing import Any


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


def _gmail_resource(credentials=None):
    if not credentials:
        raise ValueError("Credentials not provided.")

    return build("gmail", "v1", credentials=credentials)


def send_custom_email(
    message: Union[MIMEMultipart, MIMEText, MIMEImage], credentials: Any
):
    service = _gmail_resource(credentials)
    message_object = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
    return _send_message(service, message_object)

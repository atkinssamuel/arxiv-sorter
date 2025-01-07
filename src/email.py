import os
import os.path
import base64

from typing import Union
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

from_email = os.getenv("FROM_EMAIL")

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _create_text_message(subject: str, html: str, recipient: str):
    message = MIMEText(html, "html")
    message["to"] = recipient
    message["from"] = from_email
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
    service = _get_gmail_service()
    message_object = _create_text_message(subject, html, recipient)
    return _send_message(service, message_object)


def send_custom_email(message: Union[MIMEMultipart, MIMEText, MIMEImage]):
    service = _get_gmail_service()
    message_object = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}
    return _send_message(service, message_object)

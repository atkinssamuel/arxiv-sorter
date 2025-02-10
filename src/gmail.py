import os
from dotenv import load_dotenv
import requests

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open("refresh.txt", "w") as f:
        f.write(creds.refresh_token)


def refresh_token():
    if not os.path.exists("refresh.txt"):
        print("Refresh token not found. Authenticating...")
        authenticate()

    with open("refresh.txt", "r") as f:
        return f.read()


def access_token(r):
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": r,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, data=data).json()

    if "access_token" not in response:
        print(response)
        raise Exception("Access token not found")

    return response.get("access_token")


def credentials():
    r = refresh_token()

    if not r:
        raise Exception("Refresh token not found")

    t = access_token(r)

    if not t:
        raise Exception("Access token not found")

    return Credentials(
        token=t,
        refresh_token=r,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )


def gmail_resource():
    return build("gmail", "v1", credentials=credentials())

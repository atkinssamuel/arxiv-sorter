import os

from dotenv import load_dotenv
from google_auth_wrapper import authenticate

if __name__ == "__main__":
    load_dotenv()

    authenticate(scopes=[os.getenv("GOOGLE_SCOPE")])

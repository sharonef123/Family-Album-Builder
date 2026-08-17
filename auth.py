import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError

CLIENT_SECRET_FILE = r"C:\AppsProjects\MyApps\album-builder\client_secret_2_415896127616-euoecu375g31a6ibs5pnherqc43bfron.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
TOKEN_FILE = r"C:\AppsProjects\MyApps\album-builder\token.pickle"

def get_authenticated_service():
    """Authenticate with Google Photos API and return the service object."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    from googleapiclient.discovery import build
    return build('photoslibrary', 'v1', credentials=creds, static_discovery=False)

def refresh_token_if_expired():
    """Refresh the token if it's expired."""
    if not os.path.exists(TOKEN_FILE):
        return False

    with open(TOKEN_FILE, 'rb') as token:
        creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            return True
        except RefreshError:
            return False

    return creds and creds.valid

import os
import json
import base64
import pickle
import tempfile
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def get_client_secret_file():
    """Get client secret file path or create temp file from env variable."""
    if 'GOOGLE_CLIENT_SECRET_B64' in os.environ:
        secret_b64 = os.environ['GOOGLE_CLIENT_SECRET_B64']
        secret_json = base64.b64decode(secret_b64).decode('utf-8')

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write(secret_json)
        temp_file.close()

        return temp_file.name
    else:
        return r"C:\AppsProjects\MyApps\album-builder\client_secret_415896127616-nffpfqa7bhid4vrp982262bppro2metm.apps.googleusercontent.com.json"

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
            client_secret = get_client_secret_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret, SCOPES)
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

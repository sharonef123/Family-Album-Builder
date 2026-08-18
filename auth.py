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

TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".album-builder", "token.pickle")

os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)

def get_authenticated_service():
    """Authenticate with Google Photos API and return the service object."""
    print("🔐 get_authenticated_service() called", flush=True)
    creds = None

    # Check if token is in environment variable (production)
    if 'GOOGLE_OAUTH_TOKEN' in os.environ:
        print("✓ Loading token from GOOGLE_OAUTH_TOKEN env var", flush=True)
        try:
            token_data = base64.b64decode(os.environ['GOOGLE_OAUTH_TOKEN'])
            creds = pickle.loads(token_data)
            print("✓ Token loaded from env", flush=True)
        except Exception as e:
            print(f"✗ Failed to load token from env: {e}", flush=True)
            creds = None

    # Otherwise check for local token file
    if not creds:
        print(f"Checking for token file: {TOKEN_FILE}", flush=True)
        if os.path.exists(TOKEN_FILE):
            print("✓ Token file exists, loading...", flush=True)
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            print("✓ Token loaded", flush=True)
        else:
            print("✗ Token file not found", flush=True)

    if not creds or not creds.valid:
        print("Credentials invalid or missing, need OAuth", flush=True)
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing token...", flush=True)
                creds.refresh(Request())
                print("✓ Token refreshed", flush=True)
            except RefreshError:
                print("✗ Token refresh failed", flush=True)
                creds = None

        if not creds:
            print("⚠️ No valid credentials. Attempting OAuth login...", flush=True)
            try:
                client_secret = get_client_secret_file()
                print(f"Using client secret: {client_secret}", flush=True)
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret, SCOPES)
                print("Running local server for OAuth...", flush=True)
                # Use open_browser=False to avoid browser error in containerized environments
                creds = flow.run_local_server(port=0, open_browser=False)
                print("✅ OAuth successful!", flush=True)
            except Exception as e:
                print(f"❌ OAuth failed: {type(e).__name__}: {e}", flush=True)
                import traceback
                traceback.print_exc()
                raise

        print("Saving token to file...", flush=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print("✓ Token saved", flush=True)

    print("Building Google API service...", flush=True)
    from googleapiclient.discovery import build
    service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    print("✓ Service built successfully", flush=True)
    return service

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

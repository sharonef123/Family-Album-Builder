#!/usr/bin/env python3
"""
Manual OAuth flow - use this if automatic flow hangs.
"""
import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def get_client_secret_file():
    """Get client secret file path."""
    return r"C:\AppsProjects\MyApps\album-builder\client_secret_415896127616-nffpfqa7bhid4vrp982262bppro2metm.apps.googleusercontent.com.json"

print("=" * 60)
print("Manual OAuth Flow")
print("=" * 60)
print()

try:
    client_secret = get_client_secret_file()
    print(f"Using: {client_secret}")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)

    # Manual flow without automatic browser
    auth_url, _ = flow.authorization_url(prompt='consent')
    print("📋 Click this link and authorize:")
    print(auth_url)
    print()

    # Get authorization code
    code = input("Paste the authorization code from URL: ").strip()
    print()

    # Exchange code for token
    creds = flow.fetch_token(code=code)

    # Save token
    token_file = os.path.join(os.path.expanduser("~"), ".album-builder", "token.pickle")
    os.makedirs(os.path.dirname(token_file), exist_ok=True)

    with open(token_file, 'wb') as f:
        pickle.dump(creds, f)

    print("✅ Token saved!")
    print()

    # Convert to base64
    with open(token_file, 'rb') as f:
        token_data = f.read()

    token_b64 = base64.b64encode(token_data).decode('utf-8')

    print("📋 Add this to Railway Variables as GOOGLE_OAUTH_TOKEN:")
    print()
    print(token_b64)
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

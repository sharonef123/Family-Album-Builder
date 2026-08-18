#!/usr/bin/env python3
"""
Generate OAuth token locally and print as base64 for Railway env var.
Run this ONCE locally to get the token, then set it in Railway Variables.
"""
import os
import base64
import pickle
from auth import get_authenticated_service

print("=" * 60)
print("OAuth Token Generator for Railway")
print("=" * 60)
print()

# This will trigger OAuth login in browser
print("🔐 Triggering OAuth flow...")
print("   A browser will open for Google login")
print()

try:
    service = get_authenticated_service()
    print()
    print("✅ OAuth successful!")
    print()

    # Read token.pickle
    token_file = os.path.join(os.path.expanduser("~"), ".album-builder", "token.pickle")

    if os.path.exists(token_file):
        with open(token_file, 'rb') as f:
            token_data = f.read()

        # Convert to base64
        token_b64 = base64.b64encode(token_data).decode('utf-8')

        print("📋 Add this to Railway Variables as GOOGLE_OAUTH_TOKEN:")
        print()
        print(token_b64)
        print()
        print("Then restart Railway deployment.")
    else:
        print("❌ Token file not found")

except Exception as e:
    print(f"❌ OAuth failed: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
import sys
import os
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("Family Album Builder")
    print("=" * 60)
    print("\n1. Google OAuth2 Authentication...")
    print("2. Starting Flask server on port 5050...")
    print("3. Opening browser...")
    print("\nServer running at: http://localhost:5050")
    print("Press Ctrl+C to stop\n")

    webbrowser.open("http://localhost:5050")

    app.run(
        host='127.0.0.1',
        port=5050,
        debug=False,
        use_reloader=False
    )

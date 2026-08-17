#!/usr/bin/env python3
import sys
import os
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') == 'development'
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'

    print("=" * 60)
    print("Family Album Builder")
    print("=" * 60)
    print(f"\nServer running at port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}\n")

    if port == 5050:
        webbrowser.open("http://localhost:5050")

    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False
    )

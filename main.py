#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5050))
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug = flask_env == 'development'
    host = '0.0.0.0'

    print("=" * 60)
    print("Family Album Builder")
    print("=" * 60)
    print(f"\nServer running at port {port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {flask_env}\n", flush=True)

    if debug:
        import webbrowser
        webbrowser.open("http://localhost:5050")

    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False
    )

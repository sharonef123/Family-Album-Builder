import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from photos_api import sync_all_media, search_by_people, search_by_date_range, get_sync_status, download_photo
from album_generator import generate_album_pdf
import threading

app = Flask(__name__, template_folder='templates', static_folder='static')

# People list for selection
PEOPLE = [
    "רמי עפרוני", "אופיר ברקוביץ", "שרון עפרוני", "כפיר עפרוני",
    "רותם עפרוני", "נועם עפרוני", "מעה ברקוביץ", "לירון ברקוביץ",
    "דנה עפרוני", "כפיר", "דור עפרוני", "ניצן ברקוביץ",
    "אמה עפרוני", "ליה עפרוני", "לביא עפרוני", "יהב עפרוני",
    "אלון ברקוביץ", "מור עפרוני"
]

sync_progress = {'status': 'idle', 'count': 0}

@app.route('/')
def index():
    """Home page with person selection."""
    sync_count = get_sync_status()
    return render_template('index.html', people=PEOPLE, sync_count=sync_count)

@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Start media sync in background."""
    def do_sync():
        sync_progress['status'] = 'syncing'
        sync_progress['count'] = 0

        def progress_callback(count):
            sync_progress['count'] = count

        total = sync_all_media(progress_callback)
        sync_progress['status'] = 'complete'
        sync_progress['count'] = total

    thread = threading.Thread(target=do_sync)
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'started'})

@app.route('/api/sync-status', methods=['GET'])
def sync_status():
    """Get current sync status."""
    return jsonify(sync_progress)

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search for photos by people or date range."""
    data = request.json
    search_type = data.get('type', 'people')

    try:
        if search_type == 'people':
            names = data.get('names', [])
            results = search_by_people(names)
        elif search_type == 'date':
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            results = search_by_date_range(start_date, end_date)
        else:
            results = []

        return jsonify({
            'success': True,
            'count': len(results),
            'photos': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/results')
def results():
    """Results page showing found photos."""
    return render_template('results.html')

@app.route('/album-editor')
def album_editor():
    """Album editor page for arranging and customizing."""
    return render_template('album_editor.html')

@app.route('/api/generate-pdf', methods=['POST'])
def api_generate_pdf():
    """Generate PDF album from selected photos."""
    data = request.json

    try:
        selected_photos = data.get('photos', [])
        title = data.get('title', 'אלבום משפחה')
        layout = data.get('layout', '2x2')

        pdf_path = generate_album_pdf(
            selected_photos,
            title,
            layout
        )

        return jsonify({
            'success': True,
            'path': pdf_path,
            'filename': os.path.basename(pdf_path)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/download/<filename>', methods=['GET'])
def download_pdf(filename):
    """Download generated PDF."""
    output_dir = r"C:\AppsProjects\MyApps\album-builder\output"
    file_path = os.path.join(output_dir, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/download-photo', methods=['POST'])
def api_download_photo():
    """Download individual photo for preview."""
    data = request.json

    try:
        base_url = data.get('base_url')
        temp_path = r"C:\AppsProjects\MyApps\album-builder\cache\temp.jpg"

        if download_photo(base_url, temp_path):
            return send_file(temp_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Download failed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)

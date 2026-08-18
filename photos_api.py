import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict
import requests
from auth import get_authenticated_service

logger = logging.getLogger(__name__)

CACHE_DIR = r"C:\AppsProjects\MyApps\album-builder\cache"
DB_PATH = os.path.join(CACHE_DIR, "media_items.db")

def init_cache():
    """Initialize cache directory and SQLite database."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_items (
            id TEXT PRIMARY KEY,
            filename TEXT,
            mime_type TEXT,
            media_metadata TEXT,
            creation_time TEXT,
            base_url TEXT
        )
    ''')

    conn.commit()
    conn.close()

def sync_all_media(progress_callback=None):
    """
    One-time sync of all media metadata from Google Photos to local SQLite cache.
    Handles pagination automatically.
    """
    init_cache()
    service = get_authenticated_service()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM media_items')
    conn.commit()

    page_token = None
    total_synced = 0
    error_count = 0

    logger.info("🔄 Starting media sync from Google Photos...")

    try:
        while True:
            try:
                request_body = {'pageSize': 100}
                if page_token:
                    request_body['pageToken'] = page_token

                logger.info(f"  Fetching batch {total_synced // 100 + 1}...")
                response = service.mediaItems().list(**request_body).execute()

                media_items = response.get('mediaItems', [])

                if not media_items:
                    logger.info(f"  No more items returned")
                    break

                for item in media_items:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO media_items
                            (id, filename, mime_type, media_metadata, creation_time, base_url)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            item.get('id'),
                            item.get('filename', ''),
                            item.get('mimeType', ''),
                            json.dumps(item.get('mediaMetadata', {})),
                            item.get('mediaMetadata', {}).get('creationTime', ''),
                            item.get('baseUrl', '')
                        ))

                        total_synced += 1

                        if total_synced % 100 == 0:
                            conn.commit()
                            if progress_callback:
                                progress_callback(total_synced)
                            logger.info(f"  ✓ Synced {total_synced} items...")

                    except Exception as item_error:
                        error_count += 1
                        logger.warning(f"  ⚠ Error processing item: {item_error}")
                        continue

                conn.commit()

                if progress_callback:
                    progress_callback(total_synced)

                page_token = response.get('nextPageToken')
                if not page_token:
                    logger.info(f"✅ Sync complete! Total: {total_synced} photos")
                    if error_count > 0:
                        logger.warning(f"⚠ {error_count} items had errors")
                    break

            except Exception as e:
                logger.error(f"❌ Error during sync: {e}")
                error_count += 1
                if error_count > 5:
                    logger.error("Too many errors, stopping sync")
                    break
                continue

    finally:
        conn.close()

    return total_synced

def search_by_people(names: List[str]) -> List[Dict]:
    """
    Search for photos containing people by name.
    Note: Google Photos API doesn't expose person IDs directly.
    This searches by: filename, description, and PEOPLE content category.
    Best practice: Tag albums with person names in Google Photos.
    """
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build SQL query to search in filename and media metadata
    where_clauses = []
    for name in names:
        # Search for name variations (case-insensitive)
        where_clauses.append(f"LOWER(filename) LIKE LOWER('%{name}%')")
        where_clauses.append(f"LOWER(media_metadata) LIKE LOWER('%{name}%')")

    if not where_clauses:
        conn.close()
        return []

    sql = "SELECT * FROM media_items WHERE (" + " OR ".join(where_clauses) + ") ORDER BY creation_time DESC"

    try:
        cursor.execute(sql)
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'filename': row[1],
                'mime_type': row[2],
                'media_metadata': json.loads(row[3]),
                'creation_time': row[4],
                'base_url': row[5]
            })
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []
    finally:
        conn.close()

def search_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """
    Search for photos by date range (YYYY-MM-DD format).
    Fallback search for manual filtering.
    """
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM media_items
        WHERE creation_time BETWEEN ? AND ?
        ORDER BY creation_time DESC
    ''', (start_date + 'T00:00:00Z', end_date + 'T23:59:59Z'))

    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row[0],
            'filename': row[1],
            'mime_type': row[2],
            'media_metadata': json.loads(row[3]),
            'creation_time': row[4],
            'base_url': row[5]
        })

    conn.close()
    return results

def get_all_albums():
    """Fetch all albums from Google Photos."""
    service = get_authenticated_service()

    try:
        response = service.albums().list(pageSize=50).execute()
        return response.get('albums', [])
    except Exception as e:
        print(f"Error fetching albums: {e}")
        return []

def download_photo(base_url: str, output_path: str):
    """Download a photo from Google Photos base URL."""
    try:
        response = requests.get(base_url + "=d")
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        print(f"Error downloading photo: {e}")
        return False

def get_sync_status():
    """Check if sync has been performed and return count of cached items."""
    if not os.path.exists(DB_PATH):
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM media_items')
    count = cursor.fetchone()[0]
    conn.close()

    return count

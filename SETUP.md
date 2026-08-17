# Family Album Builder - Setup Guide

A Python application that searches Google Photos for family pictures and generates print-ready PDF albums.

## Features

- 🔐 Google Photos OAuth2 authentication
- 🔍 Search photos by people names or date range
- 📸 Visual interface for photo selection
- ✏️ Drag-and-drop album editor
- 📄 Print-ready PDF generation with Hebrew RTL support
- 💾 Local SQLite cache for fast searching

## Initial Setup

### 1. Install Python Dependencies

```bash
cd C:\AppsProjects\MyApps\album-builder
pip install -r requirements.txt
```

### 2. Verify Google OAuth Credentials

The `client_secret_2_415896127616-euoecu375g31a6ibs5pnherqc43bfron.apps.googleusercontent.com.json` file should already be in the project directory.

### 3. First Run

```bash
python main.py
```

This will:
1. Open your browser to http://localhost:5050
2. Prompt you to authenticate with Google
3. Display the main interface

## Usage Workflow

### Step 1: Sync Photos
- Click "התחל סנכרון" (Start Sync) button
- This downloads metadata for all photos in your Google Photos library
- Progress is shown in real-time
- Synced data is cached locally in `cache/media_items.db`

### Step 2: Search for Photos
Choose one of two search methods:

**By People:**
- Select family members from the checkbox list
- Click "חפש תמונות" (Search Photos)

**By Date:**
- Choose a date range
- Click "חפש תמונות" (Search Photos)

### Step 3: Select Photos
- Review search results
- Check photos you want in the album
- Use "בחר הכל" (Select All) for convenience
- Click "צור אלבום מהנבחרות" (Create Album)

### Step 4: Edit Album
- Drag photos to reorder them
- Add album title (Hebrew supported)
- Choose layout (1x1, 2x2, 3x3, etc.)
- Preview the arrangement

### Step 5: Export to PDF
- Click "ייצא ל-PDF" (Export to PDF)
- PDF will be generated and automatically downloaded
- Files are saved to `output/` directory

## Project Structure

```
album-builder/
├── main.py                 # Entry point
├── auth.py                 # Google OAuth2 authentication
├── photos_api.py           # Google Photos API wrapper & SQLite cache
├── album_generator.py      # PDF generation with ReportLab
├── requirements.txt        # Python dependencies
├── cache/                  # Local SQLite database
├── output/                 # Generated PDF files
├── ui/
│   ├── app.py             # Flask web server
│   ├── templates/
│   │   ├── index.html     # Main page (people selection)
│   │   ├── results.html   # Search results display
│   │   └── album_editor.html  # Photo ordering & PDF export
│   └── static/
│       └── style.css      # Styling (responsive, RTL support)
└── client_secret_*.json   # Google OAuth credentials
```

## Important Notes

### Google Photos API Limitations

- **No Direct Person ID Access**: The API doesn't expose person names/IDs directly
  - Solution: We search by filename/metadata that often contains person names
  - Manual tagging in Google Photos helps improve results

- **Pagination**: API returns max 100 items per request
  - Solution: Automatic pagination handles all photos

- **Metadata Coverage**: Not all photos have complete metadata
  - Solution: Provide date-based search as fallback

### Local Caching

- First sync downloads metadata for **all** photos (can take a few minutes)
- Subsequent searches are instant (local SQLite queries)
- Cache is stored in `cache/media_items.db`
- To re-sync, clear the cache or the app will automatically handle refresh

### PDF Generation

- Supports Hebrew text with proper RTL display
- Uses ReportLab for professional layout
- Multiple layout options for flexibility
- Photo quality optimized for print (300 DPI equivalent)
- Margins: 1cm on all sides

## Troubleshooting

### Authentication Issues
- Clear `token.pickle` file to force re-authentication
- Ensure client_secret JSON file is present

### No Photos Found
- Run sync first to populate the cache
- Try date-based search if people search doesn't work
- Check that photos are properly tagged in Google Photos

### PDF Generation Fails
- Ensure sufficient disk space
- Check `output/` directory permissions
- Verify photo URLs are accessible

### Performance Issues
- Sync takes longer on first run (depending on photo count)
- Once cached, searches are instant
- PDF generation depends on internet connection (downloads full-size photos)

## Dependencies

- **Flask**: Web framework for UI
- **google-auth**: Google OAuth authentication
- **google-api-python-client**: Google Photos API client
- **ReportLab**: PDF generation
- **Pillow**: Image processing
- **arabic-reshaper**: Hebrew text reshaping for PDFs
- **python-bidi**: Bidirectional text support for Hebrew
- **requests**: HTTP client for photo downloads

## Language Support

The entire UI is in Hebrew with RTL (Right-to-Left) support:
- All buttons and labels are Hebrew
- Responsive design works on mobile
- PDF titles and metadata support Hebrew

## License

Personal project - Use freely for family albums!

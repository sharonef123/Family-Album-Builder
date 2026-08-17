import os
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from PIL import Image as PILImage
from io import BytesIO
import requests
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import tempfile

OUTPUT_DIR = r"C:\AppsProjects\MyApps\album-builder\output"

LAYOUT_CONFIGS = {
    '1x1': (1, 1),
    '1x2': (1, 2),
    '2x1': (2, 1),
    '2x2': (2, 2),
    '3x2': (3, 2),
    '3x3': (3, 3),
}

def setup_hebrew_text(text):
    """Prepare Hebrew text for RTL rendering."""
    if not text:
        return text

    try:
        reshaped = reshape(text)
        return get_display(reshaped)
    except:
        return text

def download_and_resize_photo(base_url, max_width, max_height):
    """Download photo and resize it for PDF."""
    try:
        response = requests.get(base_url + "=d")
        response.raise_for_status()

        img = PILImage.open(BytesIO(response.content))
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=90)
        output.seek(0)

        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.write(output.getvalue())
        temp_file.close()

        return temp_file.name, img.size
    except Exception as e:
        print(f"Error processing photo: {e}")
        return None, None

def generate_album_pdf(
    selected_photos,
    title,
    layout='2x2',
    output_path=None
):
    """
    Generate a print-ready PDF album from selected photos.
    Supports RTL Hebrew text and multiple layouts.

    Args:
        selected_photos: List of dicts with 'base_url', 'filename', 'creation_time'
        title: Album title (supports Hebrew)
        layout: Layout string like '2x2', '3x3', etc.
        output_path: Path to save PDF (if None, auto-generates in output/)
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"album_{timestamp}.pdf")

    if layout not in LAYOUT_CONFIGS:
        layout = '2x2'

    cols, rows = LAYOUT_CONFIGS[layout]

    # Page setup
    page_size = landscape(A4)
    page_width, page_height = page_size

    margin = 1 * cm
    available_width = page_width - (2 * margin)
    available_height = page_height - (3 * cm)

    img_width = available_width / cols - 0.5 * cm
    img_height = available_height / rows - 0.5 * cm

    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    story = []
    styles = getSampleStyleSheet()

    # Hebrew title style
    title_style = ParagraphStyle(
        'HebrewTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#e0a82b'),
        spaceAfter=12,
        alignment=2,
    )

    # Add title
    hebrew_title = setup_hebrew_text(title)
    story.append(Paragraph(hebrew_title, title_style))
    story.append(Spacer(1, 0.3 * cm))

    # Organize photos into pages
    temp_files = []

    try:
        for page_num, page_start in enumerate(range(0, len(selected_photos), cols * rows)):
            if page_num > 0:
                story.append(PageBreak())

            page_photos = selected_photos[page_start:page_start + cols * rows]

            # Download and prepare images
            img_paths = []
            for photo in page_photos:
                img_path, size = download_and_resize_photo(
                    photo['base_url'],
                    int(img_width * 72 / 2.54),
                    int(img_height * 72 / 2.54)
                )

                if img_path:
                    img_paths.append(img_path)
                    temp_files.append(img_path)
                else:
                    img_paths.append(None)

            # Pad with None if needed
            while len(img_paths) < cols * rows:
                img_paths.append(None)

            # Create table for layout
            table_data = []
            for row_idx in range(rows):
                row_data = []
                for col_idx in range(cols):
                    idx = row_idx * cols + col_idx

                    if idx < len(img_paths) and img_paths[idx]:
                        try:
                            img = Image(
                                img_paths[idx],
                                width=img_width,
                                height=img_height
                            )
                            row_data.append(img)
                        except:
                            row_data.append('')
                    else:
                        row_data.append('')

                table_data.append(row_data)

            # Create and style table
            table = Table(
                table_data,
                colWidths=[img_width] * cols,
                rowHeights=[img_height] * rows
            )

            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))

            story.append(table)

            # Add date info at bottom
            if page_photos:
                date_str = page_photos[0].get('creation_time', '')[:10]
                date_style = ParagraphStyle(
                    'DateInfo',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=2,
                )
                story.append(Spacer(1, 0.3 * cm))
                story.append(Paragraph(f"תאריך: {date_str}", date_style))

        # Build PDF
        doc.build(story)
        print(f"Album PDF created: {output_path}")
        return output_path

    finally:
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

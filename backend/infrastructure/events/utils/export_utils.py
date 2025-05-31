import csv
import io
from typing import List, Dict, Any

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def export_to_csv(data: List[Dict[str, Any]], fieldnames: List[str]) -> str:
    """
    Export a list of dicts to CSV string.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()

def export_to_pdf(data: List[Dict[str, Any]], fieldnames: List[str], title: str = "Report") -> bytes:
    """
    Export a list of dicts to PDF bytes. Requires reportlab.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("reportlab is required for PDF export")
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 40, title)
    c.setFont("Helvetica", 10)
    y = height - 70
    row_height = 16
    # Header
    for i, field in enumerate(fieldnames):
        c.drawString(40 + i * 120, y, field)
    y -= row_height
    # Rows
    for row in data:
        for i, field in enumerate(fieldnames):
            value = str(row.get(field, ""))
            c.drawString(40 + i * 120, y, value)
        y -= row_height
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()
    return output.getvalue() 
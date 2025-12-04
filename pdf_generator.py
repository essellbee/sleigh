import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
try:
    from pypdf import PdfReader, PdfWriter
    pypdf_available = True
except ImportError:
    pypdf_available = False

def create_certificate_pdf(name, verdict, score, comment, template_path):
    """
    Generates a filled PDF certificate by overlaying text onto a base PDF.
    Assumes a Landscape Letter template.
    """
    if not pypdf_available:
        return None

    # Create a buffer for the text overlay
    packet = io.BytesIO()
    
    # Create the ReportLab canvas (Landscape)
    # Width: 792, Height: 612
    c = canvas.Canvas(packet, pagesize=landscape(letter))
    
    # Center X coordinate (11 inches * 72 points / 2)
    center_x = 396 
    
    # --- Text Overlay Logic ---
    
    # 1. The Name (Prominent, Center)
    # Moved down to y=280
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(center_x, 280, name) 
    
    # 2. The Verdict (Sleigh or Nay)
    # Moved down to y=220
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(center_x, 220, verdict)
    
    # 3. The Score
    # Moved down to y=190
    c.setFont("Helvetica", 18)
    c.drawCentredString(center_x, 190, f"Spirit Score: {score}/10")
    
    # 4. The Comment (Santa's Roast/Praise)
    # Moved down to y=160
    c.setFont("Helvetica-Oblique", 12)
    # Simple truncation to prevent overflow
    clean_comment = comment.replace('\n', ' ')
    if len(clean_comment) > 90:
        clean_comment = clean_comment[:90] + "..."
    c.drawCentredString(center_x, 160, f'"{clean_comment}"')

    c.save()
    packet.seek(0)
    
    # Merge with existing template
    try:
        if not os.path.exists(template_path):
            return packet
            
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()
        
        # Get the first page of the template
        page = existing_pdf.pages[0]
        
        # Merge the new text overlay onto the template page
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        # Write the result to a BytesIO buffer
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        return output_stream
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return None

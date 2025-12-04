import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
try:
    from pypdf import PdfReader, PdfWriter
    pypdf_available = True
except ImportError:
    pypdf_available = False

def create_certificate_pdf(name, verdict, score, comment, template_path):
    """
    Generates a filled PDF certificate by overlaying text onto a base PDF.
    """
    if not pypdf_available:
        return None

    # Create a buffer for the text overlay
    packet = io.BytesIO()
    
    # Create the ReportLab canvas
    # Note: PDF coordinates start from bottom-left
    c = canvas.Canvas(packet, pagesize=letter)
    
    # 1. Overlay the Verdict (Top Center-ish)
    c.setFont("Helvetica-Bold", 30)
    # drawCentredString centers text around the X coordinate
    c.drawCentredString(396, 420, verdict)
    
    # 2. Overlay the Score
    c.setFont("Helvetica", 20)
    c.drawCentredString(396, 380, f"Spirit Score: {score}/10")
    
    # 3. Overlay the Comment (Truncated to fit)
    c.setFont("Helvetica-Oblique", 12)
    clean_comment = comment.replace('\n', ' ')[:80] + "..." if len(comment) > 80 else comment
    c.drawCentredString(396, 350, f'"{clean_comment}"')

    # 4. Overlay the Captured Name at specific coordinates
    # Using the specific font and coordinates requested
    c.setFont("Helvetica-Bold", 24)
    # Drawing directly at x=400, y=300
    c.drawString(400, 300, name) 
    
    c.save()
    packet.seek(0)
    
    # Merge with existing template
    try:
        if not os.path.exists(template_path):
            # If template doesn't exist, just return the text layer so it doesn't crash
            return packet
            
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()
        
        # Get the first page of the template
        page = existing_pdf.pages[0]
        
        # Merge the new text overlay onto the template page
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        # Write the result to a BytesIO buffer to return to Streamlit
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        return output_stream
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        return None

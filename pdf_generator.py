import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
import textwrap

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

def create_roast_report(name, verdict, score, roast_content, pil_images):
    """
    Generates a 'Case File' PDF containing the full roast and evidence photos.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- Header ---
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, "Elf-GPT: Official Case File")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Subject: {name}")
    c.drawString(50, height - 100, f"Verdict: {verdict} (Score: {score}/10)")
    
    c.setLineWidth(1)
    c.line(50, height - 110, width - 50, height - 110)
    
    # --- Roast Content ---
    text_y = height - 140
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, text_y, "The Assessment:")
    text_y -= 20
    
    c.setFont("Helvetica", 11)
    # Simple word wrap
    wrapper = textwrap.TextWrapper(width=90) 
    lines = wrapper.wrap(roast_content)
    
    for line in lines:
        c.drawString(50, text_y, line)
        text_y -= 15
        
    text_y -= 20 # Gap before images
    
    # --- Images (Evidence) ---
    if pil_images:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, text_y, "The Evidence:")
        text_y -= 10
        
        # Grid settings
        img_width = 150
        img_height = 150
        x_start = 50
        gap = 20
        
        current_x = x_start
        current_y = text_y - img_height
        
        for img in pil_images:
            # Check page break
            if current_y < 50:
                c.showPage()
                current_y = height - 50 - img_height
                current_x = x_start
            
            try:
                # Convert PIL image to ReportLab ImageReader
                # We save to BytesIO first to ensure compatibility
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)
                
                # Draw image
                # aspect ratio preservation logic could go here, but square is simpler for grid
                c.drawImage(img_reader, current_x, current_y, width=img_width, height=img_height, preserveAspectRatio=True)
                
                # Move position
                current_x += img_width + gap
                if current_x + img_width > width - 50:
                    current_x = x_start
                    current_y -= (img_height + gap)
                    
            except Exception as e:
                print(f"Error drawing image: {e}")
                c.drawString(current_x, current_y + 75, "[Image Error]")

    c.save()
    buffer.seek(0)
    return buffer

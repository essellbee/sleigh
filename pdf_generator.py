import io
import os
import textwrap
from datetime import datetime

# Try importing ReportLab components safely
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib.utils import ImageReader
    reportlab_available = True
except ImportError:
    reportlab_available = False

try:
    from pypdf import PdfReader, PdfWriter, PageObject
    pypdf_available = True
except ImportError:
    pypdf_available = False

def create_certificate_pdf(name, verdict, score, comment, template_path):
    """
    Generates a filled PDF certificate.
    """
    if not reportlab_available or not pypdf_available:
        print("PDF Generator Error: Missing reportlab or pypdf libraries.")
        return None

    try:
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=landscape(letter))
        center_x = 396 
        
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(center_x, 280, str(name)) 
        
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(center_x, 220, str(verdict))
        
        c.setFont("Helvetica", 18)
        c.drawCentredString(center_x, 190, f"Spirit Score: {score}/10")
        
        c.setFont("Helvetica-Oblique", 12)
        clean_comment = str(comment).replace('\n', ' ')
        if len(clean_comment) > 90:
            clean_comment = clean_comment[:90] + "..."
        c.drawCentredString(center_x, 160, f'"{clean_comment}"')

        c.save()
        packet.seek(0)
        
        if not os.path.exists(template_path):
            print(f"Certificate Template missing: {template_path}")
            return packet
            
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(template_path, "rb"))
        output = PdfWriter()
        
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)
        return output_stream
        
    except Exception as e:
        print(f"Certificate Error: {e}")
        return None

def create_roast_report(name, verdict, score, roast_content, santa_comment, pil_images, template_path=None):
    """
    Generates a Single-Page 'Case File' PDF with specific layout requirements.
    """
    if not reportlab_available:
        return None

    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter # 612 x 792 points
        
        # --- Layout Constants ---
        left_margin = 50
        right_margin = 144 # 2 inches * 72 points
        top_margin = 90 # Shift down for header graphics
        
        # Calculate usable width constraint
        # Page Width (612) - Left Margin (50) - Right Margin (144) = 418 pts
        usable_width = width - left_margin - right_margin
        
        current_y = height - top_margin - 30 # Start position
        
        # --- 1. Subject & Date ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, f"Subject: {name}")
        current_y -= 15
        
        c.drawString(left_margin, current_y, f"Date: {datetime.now().strftime('%B %d, %Y')}")
        current_y -= 25 # Gap
        
        # --- 2. The Evidence (Images) ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, "The Evidence:")
        current_y -= 10
        
        if pil_images:
            # Calculate image dimensions for 5 across
            # Usable width: 418. Gaps: 4 * 5pts = 20pts. 
            # Remaining: 398. Per image: ~79pts.
            gap = 5
            img_count = min(len(pil_images), 5) # Max 5 images
            img_w = (usable_width - (gap * (img_count - 1))) / img_count
            img_h = img_w # Square thumbnails
            
            img_y_pos = current_y - img_h
            current_x = left_margin
            
            for i in range(img_count):
                try:
                    img = pil_images[i]
                    
                    # Resize/Compress Logic
                    img_copy = img.copy()
                    img_copy.thumbnail((400, 400)) # Smaller thumb
                    
                    if img_copy.mode != 'RGB':
                        img_copy = img_copy.convert('RGB')
                        
                    img_buffer = io.BytesIO()
                    img_copy.save(img_buffer, format='JPEG', quality=85)
                    img_buffer.seek(0)
                    img_reader = ImageReader(img_buffer)
                    
                    c.drawImage(img_reader, current_x, img_y_pos, width=img_w, height=img_h, preserveAspectRatio=True)
                    current_x += img_w + gap
                except Exception as e:
                    print(f"Img Error: {e}")
            
            current_y -= (img_h + 20) # Move down past images
        else:
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(left_margin, current_y - 15, "(No visual evidence submitted)")
            current_y -= 40

        # --- 3. Official Elf Assessment ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, "Official Elf Assessment:")
        current_y -= 15
        
        c.setFont("Helvetica", 10)
        # Calculate char wrap based on usable width (approx 6 pts per char for 10pt font)
        wrap_width = int(usable_width / 6) 
        wrapper = textwrap.TextWrapper(width=wrap_width)
        lines = wrapper.wrap(str(roast_content))
        
        # Limit lines to ensure single page
        if len(lines) > 20:
            lines = lines[:20]
            lines[-1] += "..."
            
        for line in lines:
            c.drawString(left_margin, current_y, line)
            current_y -= 12
            
        current_y -= 15 # Gap
        
        # --- 4. Verdict ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, f"Verdict: {verdict}")
        
        # One-liner on same line or next? "followed by" implies flow.
        # Let's put the oneliner on the next line indented or quoted
        current_y -= 15
        c.setFont("Helvetica-Oblique", 11)
        c.drawString(left_margin + 20, current_y, f"\"{santa_comment}\"")
        current_y -= 25
        
        # --- 5. Score ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, current_y, f"Score: {score}/10")

        c.save()
        buffer.seek(0)
        
        # --- Template Merging ---
        if template_path and os.path.exists(template_path) and pypdf_available:
            try:
                content_pdf = PdfReader(buffer)
                template_pdf = PdfReader(open(template_path, "rb"))
                output_page = template_pdf.pages[0]
                content_page = content_pdf.pages[0]
                output_page.merge_page(content_page)
                
                output = PdfWriter()
                output.add_page(output_page)
                
                final_stream = io.BytesIO()
                output.write(final_stream)
                final_stream.seek(0)
                return final_stream
            except Exception as e:
                print(f"Merge Failed: {e}")
                buffer.seek(0)
                return buffer
        else:
            return buffer

    except Exception as e:
        print(f"Report Error: {e}")
        return None

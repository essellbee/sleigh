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
        return None

    try:
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=landscape(letter))
        center_x = 396 
        
        # Only draw the Name as requested
        c.setFont("Times-Bold", 44)
        c.drawCentredString(center_x, 240, str(name)) 

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

def create_roast_report(name, verdict, score, roast_content, santa_comment, pil_images, template_path=None, report_date=None):
    """
    Generates a Single-Page 'Case File' PDF.
    """
    if not reportlab_available:
        return None

    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter # 612 x 792 points
        
        # --- Layout Constants ---
        left_margin = 50 
        right_margin = 72 # 1.0 inch
        
        # Vertical Shift
        shift_down = 134
        
        # Calculate usable width constraint
        usable_width = width - left_margin - right_margin
        
        current_y = height - shift_down - 30 # Start position
        
        # Determine Date string
        if report_date is None:
            report_date = datetime.now().strftime('%B %d, %Y')

        # --- 1. Subject & Date ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, f"Date: {report_date}")
        current_y -= 15
        
        c.drawString(left_margin, current_y, f"Subject: {name}")
        current_y -= 25 # Gap
        
        # --- 2. The Evidence (Images) ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, "Evidence:") 
        current_y -= 10
        
        if pil_images:
            # Force size for 2 across (for larger thumbnails)
            slots_across = 2
            gap = 10 
            
            # Calculate maximum dimensions for a single slot
            max_slot_w = ((usable_width - (gap * (slots_across - 1))) / slots_across) * 0.75
            max_slot_h = max_slot_w 
            
            # Bottom Y coordinate for the image row
            row_bottom_y = current_y - max_slot_h
            current_x = left_margin
            
            # Draw up to 2 images
            display_images = pil_images[:2]
            
            for img in display_images:
                try:
                    # 1. Resize/Compress
                    img_copy = img.copy()
                    img_copy.thumbnail((600, 600)) 
                    
                    if img_copy.mode != 'RGB':
                        img_copy = img_copy.convert('RGB')
                        
                    # 2. Calculate Scaled Dimensions
                    iw, ih = img_copy.size
                    scale = min(max_slot_w / iw, max_slot_h / ih)
                    new_w = iw * scale
                    new_h = ih * scale
                    
                    # 3. Calculate Positioning
                    draw_x = current_x 
                    draw_y = row_bottom_y + (max_slot_h - new_h) / 2
                    
                    # 4. Save to buffer
                    img_buffer = io.BytesIO()
                    img_copy.save(img_buffer, format='JPEG', quality=85)
                    img_buffer.seek(0)
                    img_reader = ImageReader(img_buffer)
                    
                    # 5. Draw
                    c.drawImage(img_reader, draw_x, draw_y, width=new_w, height=new_h, mask='auto')
                    
                    # Move to next slot
                    current_x += max_slot_w + gap
                    
                except Exception as e:
                    print(f"Img Error: {e}")
            
            current_y -= (max_slot_h + 20) # Move down past images row
        else:
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(left_margin, current_y - 15, "(No visual evidence submitted)")
            current_y -= 40

        # --- 3. Official Elf Assessment ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, "Official Elf Assessment:")
        current_y -= 15
        
        c.setFont("Helvetica", 12) 
        
        # Calculate char wrap
        wrap_width = int(usable_width / 7) 
        wrapper = textwrap.TextWrapper(width=wrap_width)
        lines = wrapper.wrap(str(roast_content))
        
        # Limit lines
        if len(lines) > 14:
            lines = lines[:14]
            lines[-1] += "..."
            
        for line in lines:
            c.drawString(left_margin, current_y, line)
            current_y -= 15 
            
        current_y -= 20 # Gap
        
        # Helper for wrapping Verdict and Santa text
        wrap_width_12 = int(usable_width / 7)
        wrapper_12 = textwrap.TextWrapper(width=wrap_width_12)

        # --- 4. Verdict ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, "Verdict:")
        current_y -= 15 
        
        c.setFont("Helvetica", 12)
        verdict_lines = wrapper_12.wrap(str(verdict))
        for line in verdict_lines:
            c.drawString(left_margin, current_y, line)
            current_y -= 15
            
        current_y -= 10 # Gap
        
        # --- 5. Santa's Commentary ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, current_y, "Santa Says:")
        current_y -= 15
        
        c.setFont("Helvetica", 12) 
        santa_lines = wrapper_12.wrap(f"\"{santa_comment}\"")
        for line in santa_lines:
            c.drawString(left_margin, current_y, line)
            current_y -= 15
            
        current_y -= 15 # Gap
        
        # --- 6. Score ---
        c.setFont("Helvetica-Bold", 12) 
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

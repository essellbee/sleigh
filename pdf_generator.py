import io
import os
import textwrap

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

def create_roast_report(name, verdict, score, roast_content, pil_images, template_path=None):
    """
    Generates a Single-Page 'Case File' PDF.
    Simplification: Assumes content fits on one page to ensure template merging works reliably.
    """
    if not reportlab_available:
        return None

    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Shift content down to accommodate header graphics
        shift_down = 90 
        
        # --- Header Text ---
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50 - shift_down, "Elf-GPT: Official Case File")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80 - shift_down, f"Subject: {name}")
        c.drawString(50, height - 100 - shift_down, f"Verdict: {verdict} (Score: {score}/10)")
        
        c.setLineWidth(1)
        c.line(50, height - 110 - shift_down, width - 50, height - 110 - shift_down)
        
        # --- Roast Content ---
        text_y = height - 140 - shift_down
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, text_y, "The Assessment:")
        text_y -= 20
        
        c.setFont("Helvetica", 11)
        wrapper = textwrap.TextWrapper(width=90) 
        lines = wrapper.wrap(str(roast_content))
        
        # Limit lines to prevent overflow into images since we are strictly single page now
        max_lines = 15
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] += "..."

        for line in lines:
            c.drawString(50, text_y, line)
            text_y -= 15
            
        text_y -= 20 
        
        # --- Images (Optimized & Limited for Single Page) ---
        if pil_images:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, text_y, "The Evidence:")
            text_y -= 10
            
            img_width = 150
            img_height = 150
            x_start = 50
            gap = 20
            
            current_x = x_start
            current_y = text_y - img_height
            
            # Limit images to what fits on one row (max 3 or 4) to guarantee single page
            # standard letter width is 612. 50 margin L, 50 margin R. 512 usable.
            # 150+20 = 170 per image. 3 images = 510. Perfect fit for 3 images.
            display_images = pil_images[:3] 
            
            for img in display_images:
                try:
                    # 1. Resize & Compress
                    img_copy = img.copy()
                    img_copy.thumbnail((800, 800)) 
                    
                    if img_copy.mode in ('RGBA', 'LA') or (img_copy.mode == 'P' and 'transparency' in img_copy.info):
                        background = ImageOps.new('RGB', img_copy.size, (255, 255, 255))
                        if img_copy.mode == 'P':
                            img_copy = img_copy.convert('RGBA')
                        background.paste(img_copy, mask=img_copy.split()[-1])
                        img_copy = background
                    elif img_copy.mode != 'RGB':
                        img_copy = img_copy.convert('RGB')
                        
                    img_buffer = io.BytesIO()
                    img_copy.save(img_buffer, format='JPEG', quality=85)
                    img_buffer.seek(0)
                    
                    # 2. Draw
                    img_reader = ImageReader(img_buffer)
                    c.drawImage(img_reader, current_x, current_y, width=img_width, height=img_height, preserveAspectRatio=True)
                    
                    current_x += img_width + gap
                        
                except Exception as img_e:
                    print(f"Image Error: {img_e}")
                    c.drawString(current_x, current_y + 75, "[Image Failed]")

        c.save()
        buffer.seek(0)
        
        # --- Template Merging (Simple Single Page) ---
        if template_path and os.path.exists(template_path) and pypdf_available:
            try:
                content_pdf = PdfReader(buffer)
                template_pdf = PdfReader(open(template_path, "rb"))
                
                # Get the Background Page (Template)
                output_page = template_pdf.pages[0]
                
                # Get the Content Page (We just generated this)
                content_page = content_pdf.pages[0]
                
                # Merge content ON TOP of template
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
            if template_path:
                print(f"Report Template missing: {template_path}")
            return buffer

    except Exception as e:
        print(f"Report Error: {e}")
        return None

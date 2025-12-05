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
    from pypdf import PdfReader, PdfWriter
    pypdf_available = True
except ImportError:
    pypdf_available = False

def create_certificate_pdf(name, verdict, score, comment, template_path):
    """
    Generates a filled PDF certificate by overlaying text onto a base PDF.
    Assumes a Landscape Letter template.
    """
    if not reportlab_available or not pypdf_available:
        print("PDF Generator Error: Missing reportlab or pypdf libraries.")
        return None

    try:
        # Create a buffer for the text overlay
        packet = io.BytesIO()
        
        # Create the ReportLab canvas (Landscape)
        # Width: 792, Height: 612
        c = canvas.Canvas(packet, pagesize=landscape(letter))
        
        # Center X coordinate (11 inches * 72 points / 2)
        center_x = 396 
        
        # --- Text Overlay Logic ---
        
        # 1. The Name (Prominent, Center)
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(center_x, 280, str(name)) 
        
        # 2. The Verdict (Sleigh or Nay)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(center_x, 220, str(verdict))
        
        # 3. The Score
        c.setFont("Helvetica", 18)
        c.drawCentredString(center_x, 190, f"Spirit Score: {score}/10")
        
        # 4. The Comment (Santa's Roast/Praise)
        c.setFont("Helvetica-Oblique", 12)
        # Simple truncation to prevent overflow
        clean_comment = str(comment).replace('\n', ' ')
        if len(clean_comment) > 90:
            clean_comment = clean_comment[:90] + "..."
        c.drawCentredString(center_x, 160, f'"{clean_comment}"')

        c.save()
        packet.seek(0)
        
        # Merge with existing template
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            # Return just the text layer if template is missing so it doesn't crash
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
        print(f"PDF Generation Error (Certificate): {e}")
        return None

def create_roast_report(name, verdict, score, roast_content, pil_images, template_path=None):
    """
    Generates a 'Case File' PDF containing the full roast and evidence photos.
    Supports overlaying onto a multi-page background template.
    Includes image compression to reduce file size.
    """
    if not reportlab_available:
        return None

    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # SHIFT DOWN: 1.25 inches * 72 points/inch = 90 points
        shift_down = 90
        
        # --- Header ---
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
        # Word wrap the roast content
        wrapper = textwrap.TextWrapper(width=90) 
        lines = wrapper.wrap(str(roast_content))
        
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
                    # Reset to top, maintaining the shift for the background template
                    current_y = height - 50 - shift_down - img_height
                    current_x = x_start
                
                try:
                    # OPTIMIZATION: Resize and Compress Image
                    img_copy = img.copy()
                    # Resize to a reasonable max dimension (e.g., 800px)
                    img_copy.thumbnail((800, 800))
                    
                    # Convert to RGB (remove alpha channel if PNG) to allow JPEG compression
                    if img_copy.mode in ('RGBA', 'LA'):
                        background = ImageOps.new('RGB', img_copy.size, (255, 255, 255))
                        background.paste(img_copy, mask=img_copy.split()[-1])
                        img_copy = background
                    elif img_copy.mode != 'RGB':
                        img_copy = img_copy.convert('RGB')
                        
                    img_buffer = io.BytesIO()
                    # Save as JPEG with 85% quality to drastically reduce size
                    img_copy.save(img_buffer, format='JPEG', quality=85)
                    img_buffer.seek(0)
                    img_reader = ImageReader(img_buffer)
                    
                    # Draw image
                    c.drawImage(img_reader, current_x, current_y, width=img_width, height=img_height, preserveAspectRatio=True)
                    
                    # Move position
                    current_x += img_width + gap
                    if current_x + img_width > width - 50:
                        current_x = x_start
                        current_y -= (img_height + gap)
                        
                except Exception as img_e:
                    print(f"Image drawing error: {img_e}")

        c.save()
        buffer.seek(0)
        
        # --- Template Merging Logic ---
        if template_path and os.path.exists(template_path) and pypdf_available:
            try:
                # Read the newly created content PDF
                content_pdf = PdfReader(buffer)
                
                # Read the background template
                template_pdf = PdfReader(open(template_path, "rb"))
                template_page = template_pdf.pages[0] # Assume template is single page background
                
                output = PdfWriter()
                
                # Iterate through all generated pages
                for i in range(len(content_pdf.pages)):
                    content_page = content_pdf.pages[i]
                    
                    # Create a blank page with template dimensions
                    output_page = output.add_blank_page(
                        width=template_page.width, 
                        height=template_page.height
                    )
                    
                    # Merge template (background)
                    output_page.merge_page(template_page)
                    
                    # Merge content (foreground)
                    output_page.merge_page(content_page)
                
                final_stream = io.BytesIO()
                output.write(final_stream)
                final_stream.seek(0)
                return final_stream
                
            except Exception as e:
                print(f"Template merge error: {e}")
                buffer.seek(0)
                return buffer # Return un-merged PDF if merge fails
        else:
            # If no template found, just return the white background PDF
            if template_path:
                print(f"Template not found: {template_path}")
            return buffer

    except Exception as e:
        print(f"PDF Generation Error (Report): {e}")
        return None

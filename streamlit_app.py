import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
import time
import random
import json
import base64
import os
import threading

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Sleigh or Nay?",
    page_icon="🎅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (The "App" Look) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@700&family=Roboto:wght@400;700&display=swap');

    /* General Background */
    html, body {
        overflow-x: hidden;
        width: 100%;
    }
    
    .stApp {
        background-color: #ffffff;
        max-width: 500px;
        margin: 0 auto;
        overflow-x: hidden;
        text-align: center;
    }

    /* Remove default top padding */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Center all text elements */
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp div {
        text-align: center;
    }

    /* 1. Custom Red Header Bar - Fixed for mobile */
    .header-container {
        background-color: #C93A3C;
        padding: 25px 0; /* Removed horizontal padding here, handled in wrapper */
        margin-top: 0;
        
        /* Breakout Logic */
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        width: 100vw;
        max-width: 100vw;
        
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 20px;
        box-sizing: border-box;
        overflow: hidden;
    }
    
    .header-logo-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between; 
        gap: 10px;
        padding: 0 5%; /* Percentage padding keeps it safe on mobile */
        width: 100%;
        max-width: 700px; /* Constrain width on desktop */
        margin: 0 auto;
        box-sizing: border-box;
    }
    
    .logo-text {
        font-family: 'Mountains of Christmas', cursive;
        color: white;
        font-size: clamp(2rem, 8vw, 3rem);
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }

    .header-logo-img {
        max-height: 60px; /* Reduced height */
        width: auto;
        max-width: 50%; /* Reduced max-width */
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
        object-fit: contain;
        flex-shrink: 1; /* Allow to shrink if needed */
    }
    
    .header-elf-img {
        max-height: 60px; /* Reduced height */
        width: auto;
        max-width: 30%; /* Reduced max-width */
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
        object-fit: contain;
        /* Removed rotation */
        flex-shrink: 1; /* Allow to shrink if needed */
    }
    
    .powered-by {
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: clamp(0.65rem, 2vw, 0.75rem);
        font-weight: 600;
        text-transform: uppercase;
        opacity: 0.95;
        margin-top: 8px;
        letter-spacing: 0.5px;
    }

    /* 2. Text Styling */
    .intro-text {
        text-align: center;
        font-family: 'Roboto', sans-serif;
        color: #333;
        font-size: clamp(0.9rem, 3vw, 1.05rem);
        margin-bottom: 25px;
        padding: 0 15px;
        line-height: 1.5;
    }

    .small-text {
        font-size: clamp(0.75rem, 2.5vw, 0.85rem);
        color: #666;
        text-align: center;
        margin: 20px 15px;
        line-height: 1.6;
        font-family: 'Courier New', monospace;
    }

    /* 3. Button Styling (Green Pill) */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(180deg, #5FBA47 0%, #4BA639 100%);
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: clamp(0.95rem, 3vw, 1.1rem);
        font-weight: 900;
        text-transform: uppercase;
        border-radius: 50px;
        padding: 15px 20px;
        border: none;
        box-shadow: 0px 6px 0px #357A2B, 0px 8px 15px rgba(0,0,0,0.2);
        transition: all 0.15s;
        letter-spacing: 0.5px;
    }

    div.stButton > button:hover {
        background: linear-gradient(180deg, #6FCA57 0%, #5BA749 100%);
        transform: translateY(-2px);
        box-shadow: 0px 8px 0px #357A2B, 0px 10px 20px rgba(0,0,0,0.25);
    }
    
    div.stButton > button:active {
        transform: translateY(3px);
        box-shadow: 0px 3px 0px #357A2B, 0px 4px 8px rgba(0,0,0,0.2);
    }

    /* Camera/Upload buttons in two-column layout */
    .camera-upload-row {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .camera-upload-row > div {
        flex: 1;
    }
    
    /* Improve caption visibility */
    .stApp p, .stApp caption, .stApp small {
        color: #555 !important;
        text-align: center;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #d4edda !important;
        color: #155724 !important;
        border: 1px solid #c3e6cb !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #fff3cd !important;
        color: #856404 !important;
        border: 1px solid #ffeaa7 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 600 !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #d1ecf1 !important;
        color: #0c5460 !important;
        border: 1px solid #bee5eb !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }

    /* Secondary Button (Grey for Share/Reset) */
    .secondary-btn > div.stButton > button {
        background: linear-gradient(180deg, #B0B0B0 0%, #909090 100%);
        box-shadow: 0px 5px 0px #606060, 0px 6px 12px rgba(0,0,0,0.2);
        font-size: 1rem;
    }
    
    .secondary-btn > div.stButton > button:hover {
        background: linear-gradient(180deg, #C0C0C0 0%, #A0A0A0 100%);
    }

    /* 4. Gold Frame Video */
    .gold-frame {
        border: 8px solid #D4AF37;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 0;
        margin: 30px 15px;
        box-shadow: 
            0 8px 20px rgba(0,0,0,0.4),
            inset 0 0 30px rgba(0,0,0,0.6),
            0 0 0 2px #B8941E,
            0 0 0 10px #D4AF37;
        position: relative;
        overflow: hidden;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .gold-frame img {
        width: 100%;
        display: block;
        border-radius: 5px;
    }

    /* 5. Result Typography */
    .verdict-title {
        font-family: 'Mountains of Christmas', cursive;
        font-size: clamp(2rem, 6vw, 2.5rem);
        text-align: center;
        line-height: 1.2;
        margin: 20px 0 15px 0;
        padding: 0 15px;
    }
    
    .elf-feedback-section {
        background: #f8f8f8;
        border-radius: 15px;
        padding: 20px 15px;
        margin: 20px 15px;
    }
    
    .elf-image-container {
        text-align: center;
        margin-bottom: 15px;
    }
    
    .elf-image-container img {
        width: 150px;
        height: auto;
        max-width: 100%;
    }
    
    .feedback-text {
        font-family: 'Roboto', sans-serif;
        font-size: clamp(0.85rem, 2.5vw, 0.95rem);
        line-height: 1.6;
        color: #222 !important;
        text-align: center;
    }
    
    .score-display {
        font-family: 'Mountains of Christmas', cursive;
        font-size: clamp(1.5rem, 5vw, 2rem);
        text-align: center;
        margin: 15px 0;
        font-weight: bold;
    }
    
    .santa-comment-box {
        margin: 20px 15px;
        padding: 20px 15px;
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        border-radius: 15px;
        border: 2px solid #ddd;
    }
    
    .santa-comment-box strong {
        font-family: 'Mountains of Christmas', cursive;
        font-size: clamp(1.1rem, 4vw, 1.3rem);
        color: #C93A3C !important;
    }
    
    .santa-comment-box em {
        font-family: 'Roboto', sans-serif;
        color: #333 !important;
        font-size: clamp(0.85rem, 2.5vw, 0.95rem);
        line-height: 1.5;
        font-style: normal;
        display: block;
        margin-top: 8px;
    }

    /* File uploader styling */
    .stFileUploader {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stFileUploader > div {
        padding: 0 !important;
    }
    
    /* Candy Cane Progress Bar */
    .progress-container {
      width: 100%;
      height: 30px;
      border-radius: 15px;
      border: 2px solid #C93A3C;
      overflow: hidden;
      background: #fff;
      box-sizing: border-box;
      margin: 10px 0;
      box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
    }

    .progress-bar {
      height: 100%;
      width: 100%;
      background: repeating-linear-gradient(
        45deg,
        #C93A3C 0px,
        #C93A3C 20px,
        #ffffff 20px,
        #ffffff 40px
      );
      /* Mathematically calculated for 40px diagonal pattern: 40 * sqrt(2) ≈ 56.57px */
      background-size: 56.57px 56.57px;
      animation: moveStripes 1s linear infinite;
    }

    @keyframes moveStripes {
      0% { background-position: 0 0; }
      100% { background-position: 56.57px 0; }
    }

    /* Hide Streamlit Branding */
    #MainMenu {display: none;}
    footer {display: none;}
    header {display: none;}
    
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'result' not in st.session_state:
    st.session_state.result = None
if 'images' not in st.session_state:
    st.session_state.images = None
if 'rotation_angles' not in st.session_state:
    st.session_state.rotation_angles = {}
if 'show_camera' not in st.session_state:
    st.session_state.show_camera = False

# --- API KEY SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY", "")

# --- FUNCTIONS ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def load_image_preserve_orientation(file):
    """Load image and preserve original orientation without auto-rotation"""
    img = Image.open(file)
    # Don't apply EXIF orientation - keep as-is
    return img

def rotate_image(img, angle):
    """Rotate image by specified angle"""
    return img.rotate(angle, expand=True)

def get_elf_verdict(images):
    """Sends images to Gemini and returns JSON verdict."""
    if not api_key:
        st.error("Missing API Key! Please set GEMINI_API_KEY in .streamlit/secrets.toml")
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

    prompt = """
    You are ELF-GPT 1.0, a sarcastic, trendy, and slightly judgmental Christmas Elf who's extremely online and fluent in both Gen-Z and Millennial culture. 
    Analyze these photo(s) for "Christmas Spirit". 
    
    Your Output must be valid JSON with the following keys:
    - "verdict_title": A short punchy title (e.g., "It's a Total SLEIGH!" or "Bah Humbug... So NAY.")
    - "score": A number between 1 and 10.
    - "roast_content": A paragraph of feedback mixing Gen-Z and Millennial slang. 
      * If the score is high (7-10): Give high praise using terms like "slay", "no cap", "bussin", "it's giving Christmas vibes", "main character energy", "living your best life", "goals AF", "chef's kiss", "periodt", "understood the assignment"
      * If the score is low (1-6): Roast them playfully using terms like "mid", "L", "not it", "big yikes", "cringe", "giving Grinch energy", "that's a no from me dawg", "oof", "this ain't it chief", "low-key embarrassing", "the bare minimum", "Netflix and no chill vibes"
      Be funny, specific to the image details, and mix both generational slang naturally. Don't force it - let it flow conversationally.
    - "santa_comment": A one-liner from Santa using either wholesome millennial phrases ("You're doing amazing, sweetie") or Gen-Z humor ("Bestie... we need to talk")
    """

    try:
        inputs = [prompt]
        for img in images:
            inputs.append(img)

        response = model.generate_content(inputs)
        text = response.text.replace('```json', '').replace('```', '')
        return json.loads(text)
    except Exception as e:
        # Avoid st.error here as it might break in threads; just return None
        print(f"Elf-GPT crashed: {e}") 
        return None

# --- MAIN UI ---

# 1. Custom Header Block
logo_html = ""
elf_html = ""

try:
    # Try to load the logo.png file
    if os.path.exists("assets/logo.png"):
        logo_base64 = get_base64_of_bin_file("assets/logo.png")
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="header-logo-img" alt="Sleigh or Nay?">'
    else:
        # Fallback to text if file missing
        logo_html = '<div class="logo-text">Sleigh or Nay?</div>'
        
    # Try to load the elf_gpt.png file
    if os.path.exists("assets/elf_gpt.png"):
        elf_base64 = get_base64_of_bin_file("assets/elf_gpt.png")
        elf_html = f'<img src="data:image/png;base64,{elf_base64}" class="header-elf-img" alt="Elf GPT">'
        
except Exception as e:
    logo_html = '<div class="logo-text">Sleigh or Nay?</div>'

st.markdown(f"""
<div class="header-container">
    <div class="header-logo-wrapper">
        {logo_html}
        {elf_html}
    </div>
    <div class="powered-by">Powered by ELF-GPT 1.0 🧝</div>
</div>
""", unsafe_allow_html=True)


# 2. Logic Controller
if st.session_state.result is None:
    # --- SCREEN 1: HOME ---
    
    st.markdown('<div class="intro-text">Santa is jumping on the AI bandwagon and outsourcing.</div>', unsafe_allow_html=True)
    
    # Button to show camera
    if not st.session_state.show_camera:
        if st.button("📸 OPEN CAMERA", use_container_width=True):
            st.session_state.show_camera = True
            st.rerun()
    else:
        # Use native Streamlit camera input
        camera_photo = st.camera_input("📸 Take a photo of your Christmas spirit!", key="camera")
        
        # Button to hide camera
        if st.button("❌ CLOSE CAMERA", use_container_width=True):
            st.session_state.show_camera = False
            st.rerun()
    
    # File uploader
    uploaded_files = st.file_uploader(
        "📁 Or upload photos from your device", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        key="file_uploader",
        help="Upload up to 5 photos"
    )

    # Combine camera photo with uploaded files
    all_files = []
    if st.session_state.show_camera and 'camera_photo' in locals() and camera_photo:
        all_files.append(camera_photo)
    if uploaded_files:
        all_files.extend(uploaded_files)

    if all_files:
        # Show thumbnails with rotation controls
        st.markdown("### Your Photos:")
        
        for idx, file in enumerate(all_files):
            # Generate unique key for this file
            # Check if this is the camera photo
            is_camera_photo = (st.session_state.show_camera and 'camera_photo' in locals() and camera_photo and file == camera_photo)
            
            if is_camera_photo:
                file_key = "camera_photo"
            else:
                # Use index for unique key since file.name might not exist for camera
                file_key = f"upload_{idx}"
            
            # Initialize rotation angle if not exists
            if file_key not in st.session_state.rotation_angles:
                st.session_state.rotation_angles[file_key] = 0
            
            # Load and display image
            img = load_image_preserve_orientation(file)
            
            # Apply rotation if any
            if st.session_state.rotation_angles[file_key] != 0:
                img = rotate_image(img, st.session_state.rotation_angles[file_key])
            
            # Display image and rotation button in columns
            col1, col2 = st.columns([4, 1])
            with col1:
                st.image(img, use_container_width=True)
            with col2:
                if st.button("🔄", key=f"rotate_{file_key}_{idx}", help="Rotate 90° counterclockwise"):
                    st.session_state.rotation_angles[file_key] = (st.session_state.rotation_angles[file_key] - 90) % 360
                    st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SUBMIT", use_container_width=True):
            if len(all_files) > 5:
                st.warning("⚠️ Limit 5 photos! The elves can only process so much...")
            else:
                # Load images with applied rotations
                pil_images = []
                for idx, file in enumerate(all_files):
                    # Check if this is the camera photo
                    is_camera_photo = (st.session_state.show_camera and 'camera_photo' in locals() and camera_photo and file == camera_photo)
                    
                    if is_camera_photo:
                        file_key = "camera_photo"
                    else:
                        file_key = f"upload_{idx}"
                    
                    img = load_image_preserve_orientation(file)
                    
                    # Apply rotation if any
                    if file_key in st.session_state.rotation_angles and st.session_state.rotation_angles[file_key] != 0:
                        img = rotate_image(img, st.session_state.rotation_angles[file_key])
                    
                    pil_images.append(img)
                
                st.session_state.images = pil_images
                
                # --- THREADED API CALL WITH ANIMATED TEXT ---
                
                progress_placeholder = st.empty()
                
                # Fun loading messages to cycle through
                loading_texts = [
                    "🎄 Elf-GPT is checking the list twice...",
                    "☕ Sipping hot cocoa to stay warm...",
                    "🦌 Asking Rudolph for a second opinion...",
                    "📏 Measuring your holiday cheer coefficient...",
                    "💡 Untangling the Christmas tree lights...",
                    "🥕 Feeding carrots to the reindeer...",
                    "❄️ analyzing snow composition...",
                    "🧝‍♂️ Consulting the High Council of Elves...",
                    "🍪 Quality testing Santa's cookies...",
                    "📜 Scanning the Naughty & Nice database..."
                ]
                
                # Container to store result from thread
                result_container = {"data": None}
                
                def run_api_call():
                    result_container['data'] = get_elf_verdict(pil_images)

                # Start API thread
                api_thread = threading.Thread(target=run_api_call)
                api_thread.start()

                # Animation loop while waiting
                msg_index = 0
                while api_thread.is_alive():
                    # Pick a message (cycle or random)
                    current_text = loading_texts[msg_index % len(loading_texts)]
                    
                    progress_placeholder.markdown(f"""
                        <div class="progress-container">
                          <div class="progress-bar"></div>
                        </div>
                        <p style="text-align: center; font-style: italic; color: #666; margin-top: 10px;">
                            {current_text}
                        </p>
                    """, unsafe_allow_html=True)
                    
                    # Wait a bit before next update
                    time.sleep(2)
                    msg_index = random.randint(0, len(loading_texts) - 1)

                # Thread finished
                api_thread.join()
                result = result_container['data']
                
                # Clear progress bar
                progress_placeholder.empty()
                
                if result:
                    st.session_state.result = result
                    # Clear rotations when submitting
                    st.session_state.rotation_angles = {}
                    st.rerun()

    # Video Frame with image
    st.markdown('<div class="gold-frame">', unsafe_allow_html=True)
    
    # Try to load the Santa frame image, fallback to text if not found
    try:
        st.image("assets/santa_frame.png", use_container_width=True)
    except:
        st.markdown("""
            <div style="position: relative; padding-top: 56.25%;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                            display: flex; align-items: center; justify-content: center;
                            font-family: 'Mountains of Christmas', cursive; font-size: 1.3rem; color: #5FBA47;">
                    🎅<br>A MESSAGE FROM<br>THE NORTH POLE
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- SCREEN 2: RESULTS ---
    
    data = st.session_state.result
    score = data.get("score", 5)
    
    # Color Logic
    is_sleigh = score >= 7
    title_color = "#C93A3C" if is_sleigh else "#5FBA47"  # Red for sleigh, green for nay
    
    # Layout: Conditional based on verdict
    if is_sleigh:
        # Sleigh: Phrase Left (Wide), Elf Right (Narrow)
        col_text, col_elf = st.columns([2, 1])
        
        with col_text:
            try:
                st.image("assets/sleigh_title.png", use_container_width=True)
            except:
                verdict_title = data.get("verdict_title", "IT'S A TOTAL SLEIGH!")
                st.markdown(f"""
                <div class="verdict-title" style="color: {title_color};">
                    {verdict_title}
                </div>
                """, unsafe_allow_html=True)
        
        with col_elf:
            try:
                st.image("assets/happy_elf.png", use_container_width=True)
            except:
                st.markdown(f"""
                <div style='font-size:6rem; text-align:center;'>🧝‍♂️😊</div>
                """, unsafe_allow_html=True)
                
    else:
        # Nay: Elf Left (Narrow), Phrase Right (Wide)
        col_elf, col_text = st.columns([1, 2])
        
        with col_elf:
            try:
                st.image("assets/grumpy_elf.png", use_container_width=True)
            except:
                st.markdown(f"""
                <div style='font-size:6rem; text-align:center;'>🧝‍♂️👎</div>
                """, unsafe_allow_html=True)
        
        with col_text:
            try:
                st.image("assets/nay_title.png", use_container_width=True)
            except:
                verdict_title = data.get("verdict_title", "BAH HUMBUG... SO NAY.")
                st.markdown(f"""
                <div class="verdict-title" style="color: {title_color};">
                    {verdict_title}
                </div>
                """, unsafe_allow_html=True)

    # 2. Feedback Section (all content below)
    # Combine content into one markdown block to prevent empty container artifact ("grey bar")
    feedback_content = f"""
    <div class="elf-feedback-section">
        <div class="feedback-text">
            {data.get("roast_content", "The elves are processing your results...")}
        </div>
        <div class="score-display" style="color: {title_color};">
            Score: {score}/10
        </div>
    </div>
    """
    st.markdown(feedback_content, unsafe_allow_html=True)

    # 3. Santa Footer
    st.markdown(f"""
    <div class="santa-comment-box">
        <strong>🎅 Santa Says:</strong><br><br>
        <em>{data.get("santa_comment", "Ho ho ho!")}</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Action Buttons
    # Use columns to center the buttons
    col_left, col_center, col_right = st.columns([1, 4, 1])

    with col_center:
        if st.button("DOWNLOAD YOUR CERTIFICATE", use_container_width=True):
             st.toast("🖨️ Printing at North Pole HQ...", icon="🎄")
             st.balloons()
             
        if st.button("POST YOUR ROAST", use_container_width=True):
            share_text = f"{verdict_title}\n\nScore: {score}/10\n\n{data.get('roast_content', '')[:100]}..."
            st.info("📋 Ready to share! (Copy the text above)")
            st.code(share_text)
        
        if st.button("START OVER", use_container_width=True):
            st.session_state.result = None
            st.session_state.images = None
            st.session_state.rotation_angles = {}
            st.session_state.show_camera = False
            st.rerun()

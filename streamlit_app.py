import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
import time
import random
import json

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
    .stApp {
        background-color: #ffffff;
        max-width: 500px;
        margin: 0 auto;
    }

    /* 1. Custom Red Header Bar */
    .header-container {
        background-color: #C93A3C;
        padding: 25px 20px;
        margin-top: -80px;
        margin-left: -100vw;
        margin-right: -100vw;
        padding-left: 100vw;
        padding-right: 100vw;
        border-bottom-left-radius: 25px;
        border-bottom-right-radius: 25px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 20px;
        position: relative;
    }
    
    .header-logo-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    
    .logo-text {
        font-family: 'Mountains of Christmas', cursive;
        color: white;
        font-size: 3rem;
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    .elf-icon {
        width: 60px;
        height: 60px;
        background: white;
        border-radius: 50%;
        padding: 5px;
    }
    
    .powered-by {
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: 0.75rem;
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
        font-size: 1.05rem;
        margin-bottom: 25px;
        padding: 0 20px;
        line-height: 1.5;
    }

    .small-text {
        font-size: 0.85rem;
        color: #666;
        text-align: center;
        margin: 20px 20px;
        line-height: 1.6;
        font-family: 'Courier New', monospace;
    }

    /* 3. Button Styling (Green Pill) */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(180deg, #5FBA47 0%, #4BA639 100%);
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: 1.1rem;
        font-weight: 900;
        text-transform: uppercase;
        border-radius: 50px;
        padding: 18px 20px;
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
        border: 10px solid #D4AF37;
        border-radius: 15px;
        background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
        padding: 0;
        margin: 30px 20px;
        box-shadow: 
            0 8px 20px rgba(0,0,0,0.4),
            inset 0 0 30px rgba(0,0,0,0.6),
            0 0 0 2px #B8941E,
            0 0 0 12px #D4AF37;
        position: relative;
        overflow: hidden;
    }
    
    .gold-frame img {
        width: 100%;
        display: block;
        border-radius: 5px;
    }
    
    .gold-frame-label {
        position: absolute;
        bottom: 15px;
        left: 0;
        right: 0;
        font-size: 0.75rem;
        font-family: 'Mountains of Christmas', cursive;
        color: #5FBA47;
        text-transform: uppercase;
        text-align: center;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }

    /* 5. Result Typography */
    .verdict-title {
        font-family: 'Mountains of Christmas', cursive;
        font-size: 2.5rem;
        text-align: center;
        line-height: 1.2;
        margin: 20px 0 15px 0;
        padding: 0 20px;
    }
    
    .elf-feedback-section {
        background: #f8f8f8;
        border-radius: 15px;
        padding: 20px;
        margin: 20px;
    }
    
    .elf-image-container {
        text-align: center;
        margin-bottom: 15px;
    }
    
    .elf-image-container img {
        width: 150px;
        height: auto;
    }
    
    .feedback-text {
        font-family: 'Roboto', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #222 !important;
        text-align: center;
    }
    
    .score-display {
        font-family: 'Mountains of Christmas', cursive;
        font-size: 2rem;
        text-align: center;
        margin: 15px 0;
        font-weight: bold;
    }
    
    .santa-comment-box {
        margin: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        border-radius: 15px;
        border: 2px solid #ddd;
    }
    
    .santa-comment-box strong {
        font-family: 'Mountains of Christmas', cursive;
        font-size: 1.3rem;
        color: #C93A3C !important;
    }
    
    .santa-comment-box em {
        font-family: 'Roboto', sans-serif;
        color: #333 !important;
        font-size: 0.95rem;
        line-height: 1.5;
        font-style: normal;
        display: block;
        margin-top: 8px;
    }

    /* File uploader styling - make it look like standard button */
    .stFileUploader {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stFileUploader > div {
        padding: 0 !important;
    }
    
    .stFileUploader > label > div > div > p {
        display: none !important;
    }
    
    /* Style the file uploader button container */
    [data-testid="stFileUploadDropzone"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        min-height: auto !important;
    }
    
    [data-testid="stFileUploadDropzone"] > div {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    
    /* Style the actual "Browse files" button to match our green buttons */
    [data-testid="stFileUploadDropzone"] button {
        width: 100% !important;
        background: linear-gradient(180deg, #5FBA47 0%, #4BA639 100%) !important;
        color: white !important;
        font-family: 'Roboto', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border-radius: 50px !important;
        padding: 18px 20px !important;
        border: none !important;
        box-shadow: 0px 6px 0px #357A2B, 0px 8px 15px rgba(0,0,0,0.2) !important;
        transition: all 0.15s !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
    }
    
    [data-testid="stFileUploadDropzone"] button:hover {
        background: linear-gradient(180deg, #6FCA57 0%, #5BA749 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 0px #357A2B, 0px 10px 20px rgba(0,0,0,0.25) !important;
    }
    
    [data-testid="stFileUploadDropzone"] button:active {
        transform: translateY(3px) !important;
        box-shadow: 0px 3px 0px #357A2B, 0px 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Hide the icon inside the button */
    [data-testid="stFileUploadDropzone"] button svg {
        display: none !important;
    }
    
    /* Style the text */
    [data-testid="stFileUploadDropzone"] button span {
        color: white !important;
        font-weight: 900 !important;
    }
    
    /* Hide drag and drop text */
    [data-testid="stFileUploadDropzone"] small {
        display: none !important;
    }
    
    /* Make sure uploaded file list is visible and styled */
    [data-testid="stFileUploader"] section {
        background: #f8f8f8 !important;
        padding: 10px !important;
        border-radius: 10px !important;
        margin-top: 10px !important;
        border: 1px solid #ddd !important;
    }
    
    [data-testid="stFileUploader"] section button {
        color: #333 !important;
        background: #e0e0e0 !important;
        padding: 5px 10px !important;
        border-radius: 5px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: none !important;
        box-shadow: none !important;
        border: 1px solid #ccc !important;
    }
    
    [data-testid="stFileUploader"] section button:hover {
        background: #d0d0d0 !important;
        transform: none !important;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'result' not in st.session_state:
    st.session_state.result = None
if 'images' not in st.session_state:
    st.session_state.images = None
if 'rotation_angles' not in st.session_state:
    st.session_state.rotation_angles = {}

# --- SIDEBAR (API KEY) ---
with st.sidebar:
    st.title("⚙️ Elf Settings")
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.caption("Get one at aistudio.google.com")

# --- FUNCTIONS ---
def get_elf_verdict(images):
    """Sends images to Gemini and returns JSON verdict."""
    if not api_key:
        st.error("Please provide an API Key in the sidebar settings!")
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
        st.error(f"Elf-GPT crashed: {e}")
        return None

def load_image_preserve_orientation(file):
    """Load image and preserve original orientation without auto-rotation"""
    img = Image.open(file)
    # Don't apply EXIF orientation - keep as-is
    return img

def rotate_image(img, angle):
    """Rotate image by specified angle"""
    return img.rotate(angle, expand=True)

# --- MAIN UI ---

# 1. Custom Header Block
st.markdown("""
<div class="header-container">
    <div class="header-logo-wrapper">
        <div class="logo-text">Sleigh or Nay?</div>
    </div>
    <div class="powered-by">Powered by ELF-GPT 1.0 🧝</div>
</div>
""", unsafe_allow_html=True)


# 2. Logic Controller
if st.session_state.result is None:
    # --- SCREEN 1: HOME ---
    
    st.markdown('<div class="intro-text">Santa is jumping on the AI bandwagon and outsourcing.</div>', unsafe_allow_html=True)
    
    # Camera and Upload buttons side by side
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.show_camera and not st.session_state.camera_photo:
            if st.button("📸 TAKE PHOTO", use_container_width=True):
                st.session_state.show_camera = True
                st.rerun()
        elif st.session_state.camera_photo:
            if st.button("📸 RETAKE", use_container_width=True):
                st.session_state.camera_photo = None
                st.session_state.show_camera = True
                st.rerun()
    
    with col2:
        # This is a placeholder - the actual file uploader will be below
        if st.button("📁 BROWSE FILES", use_container_width=True, key="browse_trigger"):
            # This button is just for visual consistency
            # The actual file uploader below handles the functionality
            pass
    
    # Show camera input only when toggled
    if st.session_state.show_camera:
        st.markdown("### 📸 Smile for the camera!")
        camera_photo = st.camera_input("", key="camera", label_visibility="collapsed")
        if camera_photo:
            st.session_state.camera_photo = camera_photo
            st.session_state.show_camera = False
            st.rerun()
        
        # Option to grant camera access if blocked
        st.caption("🔒 Camera blocked? Check your browser settings or refresh the page to grant access.")
    
    # Show captured photo thumbnail
    if st.session_state.camera_photo:
        st.success("✅ Photo captured!")
        camera_img = load_image_preserve_orientation(st.session_state.camera_photo)
        
        # Get rotation angle for camera photo
        camera_key = "camera_photo"
        if camera_key not in st.session_state.rotation_angles:
            st.session_state.rotation_angles[camera_key] = 0
        
        # Apply rotation if any
        if st.session_state.rotation_angles[camera_key] != 0:
            camera_img = rotate_image(camera_img, st.session_state.rotation_angles[camera_key])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image(camera_img, caption="Your photo", width=200)
        with col2:
            if st.button("🔄", key="rotate_camera", help="Rotate photo 90°"):
                st.session_state.rotation_angles[camera_key] = (st.session_state.rotation_angles[camera_key] - 90) % 360
                st.rerun()
    
    # File uploader (styled to match buttons)
    uploaded_files = st.file_uploader(
        "📁 Browse for Photos", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        help="Upload up to 5 photos",
        label_visibility="collapsed"
    )

    # Combine camera photo with uploaded files
    all_files = []
    if st.session_state.camera_photo:
        all_files.append(st.session_state.camera_photo)
    if uploaded_files:
        all_files.extend(uploaded_files)

    if all_files:
        # Show thumbnails with rotation controls
        st.markdown("### Your Photos:")
        
        for idx, file in enumerate(all_files):
            # Generate unique key for this file
            if camera_photo and file == camera_photo:
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
                    if camera_photo and file == camera_photo:
                        file_key = "camera_photo"
                    else:
                        file_key = f"upload_{idx}"
                    
                    img = load_image_preserve_orientation(file)
                    
                    # Apply rotation if any
                    if file_key in st.session_state.rotation_angles and st.session_state.rotation_angles[file_key] != 0:
                        img = rotate_image(img, st.session_state.rotation_angles[file_key])
                    
                    pil_images.append(img)
                
                st.session_state.images = pil_images
                
                # Show spinner while processing
                with st.spinner("🎄 Elf-GPT is analyzing your Christmas spirit... Please wait!"):
                    # Actually call the API (this is where the real time is spent)
                    result = get_elf_verdict(pil_images)
                
                if result:
                    st.session_state.result = result
                    # Clear rotations when submitting
                    st.session_state.rotation_angles = {}
                    st.rerun()
    
    st.markdown("""
    <div class="small-text">
        Manual judgment is unscalable. I replaced 4,000 elves with this AI. 
        Upload your data for immediate Q4 processing.
    </div>
    """, unsafe_allow_html=True)

    # Video Frame with image
    st.markdown('<div class="gold-frame">', unsafe_allow_html=True)
    
    # Using the Santa image you provided
    # You'll need to save image 2 as "santa_frame.png" in your Streamlit directory
    # For now, showing placeholder
    st.markdown("""
        <div style="position: relative; padding-top: 56.25%;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        display: flex; align-items: center; justify-content: center;
                        font-family: 'Mountains of Christmas', cursive; font-size: 1.3rem; color: white;">
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
    
    # Determine which elf image to use (you'll need to save these as files)
    # For now using emoji, but replace with: st.image("happy_elf.png") or st.image("grumpy_elf.png")
    elf_emoji = "🧝‍♂️😊" if is_sleigh else "🧝‍♂️👎"

    # 1. The Verdict Title
    verdict_title = data.get("verdict_title", "THE VERDICT")
    st.markdown(f"""
    <div class="verdict-title" style="color: {title_color};">
        {verdict_title}
    </div>
    """, unsafe_allow_html=True)

    # 2. Elf Feedback Section
    st.markdown('<div class="elf-feedback-section">', unsafe_allow_html=True)
    
    # Elf Image (centered)
    st.markdown(f"""
    <div class="elf-image-container">
        <div style='font-size:6rem;'>{elf_emoji}</div>
    </div>
    """, unsafe_allow_html=True)
    # To use actual images: st.image("happy_elf.png" if is_sleigh else "grumpy_elf.png", width=200)
    
    # Feedback text
    st.markdown(f"""
    <div class="feedback-text">
        {data.get("roast_content", "The elves are processing your results...")}
    </div>
    """, unsafe_allow_html=True)
    
    # Score
    st.markdown(f"""
    <div class="score-display" style="color: {title_color};">
        Score: {score}/10
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Santa Footer
    st.markdown(f"""
    <div class="santa-comment-box">
        <strong>🎅 Santa Says:</strong><br><br>
        <em>{data.get("santa_comment", "Ho ho ho!")}</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Action Buttons
    if st.button("DOWNLOAD YOUR CERTIFICATE"):
         st.toast("🖨️ Printing at North Pole HQ...", icon="🎄")
         st.balloons()
         
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("POST YOUR ROAST"):
        share_text = f"{verdict_title}\n\nScore: {score}/10\n\n{data.get('roast_content', '')[:100]}..."
        st.info("📋 Ready to share! (Copy the text above)")
        st.code(share_text)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("START OVER"):
        st.session_state.result = None
        st.session_state.images = None
        st.session_state.rotation_angles = {}
        st.rerun()

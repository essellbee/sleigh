import streamlit as st
import google.generativeai as genai
from PIL import Image
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
        color: #333;
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
        color: #C93A3C;
    }
    
    .santa-comment-box em {
        font-family: 'Roboto', sans-serif;
        color: #555;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        padding: 20px;
    }
    
    [data-testid="stFileUploader"] label {
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        color: #333;
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
    You are ELF-GPT 1.0, a sarcastic, trendy, and slightly judgmental Christmas Elf. 
    Analyze these photo(s) for "Christmas Spirit". 
    
    Your Output must be valid JSON with the following keys:
    - "verdict_title": A short punchy title (e.g., "It's a Total SLEIGH!" or "Bah Humbug... So NAY.")
    - "score": A number between 1 and 10.
    - "roast_content": A paragraph of feedback. If the score is high (7-10), give high praise with Gen-Z slang. If the score is low (1-6), roast them playfully about their lack of effort, sad decorations, or awkward posing. Be funny, specific to the image details.
    - "santa_comment": A one-liner from Santa.
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

def loading_animation():
    placeholders = [
        "Consulting the High Council of Elves...",
        "Judging your tinsel placement...",
        "Elf-GPT is analyzing sparkle density...",
        "Checking the Naughty List..."
    ]
    bar = st.progress(0)
    status = st.empty()
    for i in range(100):
        if i % 25 == 0:
            status.markdown(f"**{random.choice(placeholders)}**")
        bar.progress(i + 1)
        time.sleep(0.02)
    bar.empty()
    status.empty()

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
    
    uploaded_files = st.file_uploader(
        "📸 Upload Photo Evidence (Room, Tree, You...)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        help="Upload up to 5 photos of your Christmas spirit!"
    )

    if uploaded_files:
        # Show thumbnails
        cols = st.columns(min(len(uploaded_files), 3))
        for idx, file in enumerate(uploaded_files[:3]):
            with cols[idx % 3]:
                img = Image.open(file)
                st.image(img, use_container_width=True)
        
        if len(uploaded_files) > 3:
            st.caption(f"+ {len(uploaded_files) - 3} more photo(s)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SUBMIT"):
            if len(uploaded_files) > 5:
                st.warning("⚠️ Limit 5 photos! The elves can only process so much...")
            else:
                pil_images = [Image.open(f) for f in uploaded_files]
                st.session_state.images = pil_images
                loading_animation()
                result = get_elf_verdict(pil_images)
                if result:
                    st.session_state.result = result
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
        st.rerun()

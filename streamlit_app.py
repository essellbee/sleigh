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
    layout="centered", # vital for mobile-first feel
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (The "App" Look) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Mountains+of+Christmas:wght@700&family=Roboto:wght@400;700&display=swap');

    /* General Background */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Titles and Headers */
    h1 {
        font-family: 'Mountains of Christmas', cursive;
        color: #D42426; /* Christmas Red */
        text-align: center;
        font-size: 3.5rem !important;
        margin-bottom: 0px;
        text-shadow: 2px 2px 4px #00000020;
    }
    
    .subtitle {
        text-align: center;
        color: #2F5C34; /* Elf Green */
        font-weight: bold;
        margin-top: -15px;
        margin-bottom: 30px;
        font-family: 'Roboto', sans-serif;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 1.5px;
    }

    /* Buttons */
    div.stButton > button {
        width: 100%;
        background-color: #228B22; /* Forest Green */
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        padding: 15px 20px;
        border: none;
        box-shadow: 0px 4px 0px #155e15; /* 3D effect */
        transition: all 0.2s;
    }

    div.stButton > button:hover {
        background-color: #2cb52c;
        transform: translateY(-2px);
    }
    
    div.stButton > button:active {
        transform: translateY(2px);
        box-shadow: 0px 1px 0px #155e15;
    }

    /* Secondary Button (Red) */
    .red-button > div.stButton > button {
        background-color: #D42426;
        box-shadow: 0px 4px 0px #961214;
    }
    .red-button > div.stButton > button:hover {
        background-color: #ff3336;
    }

    /* Card Containers */
    .result-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 20px;
        border: 2px solid #e0e0e0;
    }

    .verdict-header {
        font-family: 'Mountains of Christmas', cursive;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .score-display {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        color: #D42426;
        margin: 10px 0;
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
    
    # Try to get key from secrets, otherwise ask user
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
    # Using the flash model for speed
    model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')

    prompt = """
    You are ELF-GPT 1.0, a sarcastic, trendy, and slightly judgmental Christmas Elf. 
    Analyze these photo(s) for "Christmas Spirit". 
    
    Your Output must be valid JSON with the following keys:
    - "verdict_title": A short punchy title (e.g., "It's a Total SLEIGH!" or "Bah Humbug... So NAY.")
    - "score": A number between 1 and 10.
    - "roast_content": A paragraph of feedback. If the score is high (7-10), give high praise with Gen-Z slang. If the score is low (1-6), roast them playfully about their lack of effort, sad decorations, or awkward posing. Be funny, specific to the image details, and mention things like 'Dad's hat' or 'the sad tinsel'.
    - "santa_comment": A one-liner from Santa (e.g., "Santa Says: A TikTok dance tutorial for the 'Renegade' circa 2019").
    """

    try:
        # Prepare inputs: Prompt + Images
        inputs = [prompt]
        for img in images:
            inputs.append(img)

        response = model.generate_content(inputs)
        
        # Clean up JSON string if markdown is included
        text = response.text.replace('```json', '').replace('```', '')
        return json.loads(text)
    except Exception as e:
        st.error(f"Elf-GPT crashed (too much eggnog): {e}")
        return None

def loading_animation():
    """Shows festive loading messages."""
    placeholders = [
        "Consulting the High Council of Elves...",
        "Checking the Naughty List database...",
        "Judging your tinsel placement...",
        "Elf-GPT is analyzing sparkle density...",
        "Measuring cheer levels..."
    ]
    bar = st.progress(0)
    status = st.empty()
    
    for i in range(100):
        if i % 20 == 0:
            status.text(random.choice(placeholders))
        bar.progress(i + 1)
        time.sleep(0.02)
    
    bar.empty()
    status.empty()

# --- MAIN UI ---

# 1. Header
st.title("Sleigh or Nay?")
st.markdown('<div class="subtitle">POWERED BY ELF-GPT 1.0 🧝</div>', unsafe_allow_html=True)

# 2. Logic Controller
if st.session_state.result is None:
    # --- INPUT SCREEN ---
    st.markdown("""
    **Santa is jumping on the AI bandwagon and outsourcing.**
    
    Manual judgment is unscalable. I replaced 4,000 elves with this AI. 
    Upload your holiday data (Room, Tree, You...) for immediate Q4 processing.
    """)
    
    uploaded_files = st.file_uploader(
        "Upload Photo Evidence (Max 5)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if len(uploaded_files) > 5:
            st.warning("Whoa there! Only 5 photos allowed. Santa's servers are busy.")
        else:
            if st.button("SUBMIT EVIDENCE"):
                # Convert uploaded files to PIL Images for Gemini
                pil_images = [Image.open(f) for f in uploaded_files]
                st.session_state.images = pil_images # Save for display later
                
                loading_animation()
                result = get_elf_verdict(pil_images)
                
                if result:
                    st.session_state.result = result
                    st.rerun()

else:
    # --- RESULT SCREEN ---
    
    # Extract Data
    data = st.session_state.result
    
    # Determine color based on score
    score = data.get("score", 5)
    score_color = "#228B22" if score >= 7 else "#D42426" # Green if good, Red if bad
    
    # Display Images (Small Carousel or Grid)
    st.image(st.session_state.images, width=100, caption=["Evidence"]*len(st.session_state.images))

    # The Card
    st.markdown(f"""
    <div class="result-card">
        <div class="verdict-header" style="color: {score_color};">
            {data.get("verdict_title", "THE VERDICT")}
        </div>
        <div class="score-display">
            SCORE: {score}/10
        </div>
        <p style="font-size: 1.1rem; line-height: 1.5; color: #333;">
            {data.get("roast_content", "No roast generated.")}
        </p>
        <hr style="border-top: 1px dashed #ccc;">
        <p style="font-style: italic; color: #666; font-size: 0.9rem;">
            <strong>🎅 Santa Says:</strong><br>
            {data.get("santa_comment", "Ho Ho No.")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write("") # Spacing
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # We can't actually trigger a native OS share easily in web, 
        # so we copy text to clipboard or just refresh
        st.markdown('<div class="red-button">', unsafe_allow_html=True)
        if st.button("Try Again"):
            st.session_state.result = None
            st.session_state.images = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Mock "Certificate" - in a real app this would download a PDF or Image
        if st.button("Get Certificate"):
            st.toast("Certificate sent to the North Pole Printer! (Check your Downloads folder in spirit)", icon="🖨️")
            st.balloons()
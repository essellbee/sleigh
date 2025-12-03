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
        background-color: #ffffff;
    }

    /* 1. Custom Red Header Bar */
    .header-container {
        background-color: #D42426;
        padding: 20px 10px;
        margin-top: -60px; /* Pull it up to top */
        margin-left: -50px; /* Stretch to edges */
        margin-right: -50px;
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        margin-bottom: 30px;
    }
    
    .logo-text {
        font-family: 'Mountains of Christmas', cursive;
        color: white;
        font-size: 3.5rem;
        line-height: 1;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.2);
    }
    
    .powered-by {
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        opacity: 0.9;
        margin-top: 5px;
    }

    /* 2. Text Styling */
    .intro-text {
        text-align: center;
        font-family: 'Roboto', sans-serif;
        color: #333;
        font-size: 1rem;
        margin-bottom: 20px;
    }

    .small-text {
        font-size: 0.9rem;
        color: #666;
        text-align: center;
        margin-top: 10px;
        line-height: 1.4;
    }

    /* 3. Button Styling (Green Pill) */
    div.stButton > button {
        width: 100%;
        background-color: #4CAF50; /* Bright Green */
        color: white;
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        font-weight: 900;
        text-transform: uppercase;
        border-radius: 50px; /* Pill shape */
        padding: 15px 20px;
        border: none;
        box-shadow: 0px 5px 0px #2E7D32; /* Deep green shadow */
        transition: all 0.2s;
    }

    div.stButton > button:hover {
        background-color: #66BB6A;
        transform: translateY(-2px);
    }
    
    div.stButton > button:active {
        transform: translateY(2px);
        box-shadow: 0px 2px 0px #2E7D32;
    }

    /* Secondary Button (Grey/Red for Share) */
    .secondary-btn > div.stButton > button {
        background-color: #9E9E9E;
        box-shadow: 0px 4px 0px #616161;
        font-size: 1rem;
    }

    /* 4. Gold Frame Video Placeholder */
    .gold-frame {
        border: 8px solid #FFD700; /* Gold */
        border-radius: 10px;
        background-color: #000;
        color: white;
        padding: 40px;
        text-align: center;
        font-family: 'Mountains of Christmas', cursive;
        font-size: 1.5rem;
        margin-top: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3), inset 0 0 20px rgba(0,0,0,0.5);
        position: relative;
    }
    
    /* Frame detailing */
    .gold-frame::before {
        content: "🎅 A MESSAGE FROM THE NORTH POLE";
        position: absolute;
        bottom: 10px;
        left: 0;
        right: 0;
        font-size: 0.8rem;
        font-family: 'Roboto', sans-serif;
        color: #FFD700;
        text-transform: uppercase;
    }

    /* 5. Result Typography */
    .verdict-title {
        font-family: 'Mountains of Christmas', cursive;
        font-size: 3rem;
        text-align: center;
        line-height: 1.1;
        margin-bottom: 10px;
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
    <div class="logo-text">Sleigh or Nay?</div>
    <div class="powered-by">Powered by ELF-GPT 1.0 🧝</div>
</div>
""", unsafe_allow_html=True)


# 2. Logic Controller
if st.session_state.result is None:
    # --- SCREEN 1: HOME ---
    
    st.markdown('<div class="intro-text">Santa is jumping on the AI bandwagon and outsourcing.</div>', unsafe_allow_html=True)
    
    # Custom File Uploader Label hack isn't easy in Streamlit, so we use standard uploader but style the button below it
    uploaded_files = st.file_uploader(
        "Upload Photo Evidence (Room, Tree, You...)", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SUBMIT EVIDENCE"):
            if len(uploaded_files) > 5:
                st.warning("Limit 5 photos!")
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

    # Video Placeholder
    st.markdown("""
    <div class="gold-frame">
        ▶<br>
        <div style="font-size: 0.8rem; margin-top: 10px; font-family:'Roboto'">VIDEO LOADING...</div>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- SCREEN 2: RESULTS ---
    
    data = st.session_state.result
    score = data.get("score", 5)
    
    # Color Logic
    is_sleigh = score >= 7
    title_color = "#228B22" if is_sleigh else "#D42426"
    elf_emoji = "🧝‍♂️" if is_sleigh else "😤" # Replace with st.image(your_elf_png) later

    # 1. The Verdict Title
    st.markdown(f"""
    <div class="verdict-title" style="color: {title_color};">
        {data.get("verdict_title", "THE VERDICT")}
    </div>
    """, unsafe_allow_html=True)

    # 2. Layout: Elf + Text
    # We use columns to mimic the 'Elf talking' layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Placeholder for Elf Image
        st.markdown(f"<div style='font-size:4rem; text-align:center;'>{elf_emoji}</div>", unsafe_allow_html=True)
        # st.image("happy_elf.png") # Uncomment when you have assets
        
    with col2:
        st.markdown(f"""
        <div style="font-family: 'Roboto'; font-size: 0.95rem; line-height: 1.4;">
            {data.get("roast_content")}
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:{title_color}; margin: 5px 0;'>Score: {score}/10</h2>", unsafe_allow_html=True)

    # 3. Santa Footer
    st.markdown(f"""
    <div style="margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 10px;">
        <strong>🎅 Santa Says:</strong><br>
        <em style="color: #555;">{data.get("santa_comment")}</em>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 
    
    # 4. Action Buttons
    if st.button("DOWNLOAD YOUR CERTIFICATE"):
         st.toast("Printing at North Pole HQ...", icon="🖨️")
         st.balloons()
         
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("Post Your Roast"):
        st.info("Copied to clipboard! (Not really, browsers block that, but pretend!)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Start Over"):
        st.session_state.result = None
        st.session_state.images = None
        st.rerun()

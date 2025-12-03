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

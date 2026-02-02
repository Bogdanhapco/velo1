import streamlit as st
from gradio_client import Client
import os

# --- 1. CONFIGURATION ---
# PASTE YOUR PINOKIO / GRADIO LINK HERE
FIXED_GRADIO_URL = "https://b2eca5eb64757141e9.gradio.live" 

st.set_page_config(page_title="Velo 1", page_icon="🎬", layout="centered")
st.title("🎬 AI Video Generator")
st.caption("Powered by Velo 1")

# --- 2. SMART SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Video Settings")
    
    # Step 1: User picks Resolution
    quality = st.select_slider("Quality", options=["480p", "720p", "1080p"], value="720p")
    
    # Step 2: LOGIC - Change options based on Resolution
    if quality == "1080p":
        st.warning("⚠️ 1080p is limited to save GPU memory because of current model training")
        # Forced options for 1080p
        aspect = st.selectbox("Aspect Ratio", ["9:16 (TikTok/Reels)"]) # Only one option
        duration = st.slider("Duration (Seconds)", min_value=5, max_value=10, value=10, disabled=True) # Locked at 10
        
    else:
        # Free options for 480p / 720p
        aspect = st.radio("Aspect Ratio", ["16:9 (Wide)", "9:16 (Tall)", "1:1 (Square)"]) 
        duration = st.slider("Duration (Seconds)", min_value=5, max_value=15, value=10)

    st.divider()
    st.markdown(f"**Status:** Connected ✅")

# --- 3. MAIN INTERFACE ---
prompt = st.text_area("Describe your video:", "A cinematic drone shot of a futuristic city...", height=120)
generate_btn = st.button("Generate Video", type="primary", use_container_width=True)

if generate_btn:
    if not FIXED_GRADIO_URL or "your-link-here" in FIXED_GRADIO_URL:
        st.error("🚨 Data Center is down!")
        st.stop()

    status_box = st.status("🚀 Connecting to GPU...", expanded=True)
    
    try:
        client = Client(FIXED_GRADIO_URL)
        status_box.write(f"⏳ Processing: {quality}, {aspect}, {duration}s...")
        
        # NOTE: Check your 'View API' link! 
        # You might need to change 'seconds' to 'length', 'duration', or 'video_length'
        result = client.predict(
            prompt,           
            quality,          
            aspect,
            duration,         # We now pass the duration too!
            api_name="/predict" 
        )
        
        status_box.update(label="✅ Complete!", state="complete", expanded=False)
        st.video(result)
        
        with open(result, "rb") as f:
            st.download_button(
                label="📥 Download MP4",
                data=f,
                file_name="ai_video.mp4",
                mime="video/mp4",
                use_container_width=True
            )

    except Exception as e:
        status_box.update(label="❌ Error", state="error")
        st.error(f"Error: {e}")

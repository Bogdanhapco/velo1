import streamlit as st
from gradio_client import Client
import os

# --- 1. CONFIGURATION ---
# IMPORTANT: Update this link every time you restart Pinokio
FIXED_GRADIO_URL = "https://1bf0f78eea4ed01e04.gradio.live" 

st.set_page_config(page_title="Velo 1", page_icon="🎥", layout="centered")
st.title("🎥 Velo 1")
st.caption("AI Video Generation - High Performance")

# --- 2. SMART SIDEBAR (LTX-2 LOGIC) ---
with st.sidebar:
    st.header("⚙️ Render Settings")
    
    quality = st.select_slider("Resolution", options=["480p", "720p", "1080p"], value="720p")
    
    if quality == "1080p":
        st.warning("⚠️ 1080p locked to 9:16 and 10s to prevent H100's crashing because of current model training")
        aspect = "9:16"
        duration = 10 
    else:
        aspect = st.radio("Aspect Ratio", ["16:9", "9:16", "1:1"])
        duration = st.slider("Duration (Seconds)", 5, 15, 10)

    st.divider()
    st.info("Queue is active. Your request will process as soon as 2 H100's is free.")

# --- 3. MAIN INTERFACE ---
prompt = st.text_area("Video Prompt:", "A cinematic shot of a red car driving through a forest, high detail, 4k", height=100)
negative_prompt = st.text_input("Negative Prompt (Optional):", "blurry, low quality, distorted")

generate_btn = st.button("Generate Video", type="primary", use_container_width=True)

if generate_btn:
    if not FIXED_GRADIO_URL or "your-link" in FIXED_GRADIO_URL:
        st.error("Owner must update the Gradio Link!")
        st.stop()

    status = st.status("🚀 Initializing Velo 1 Engine...", expanded=True)
    
    try:
        # Connect to your PC
        client = Client(FIXED_GRADIO_URL)
        status.write("⏳ Waiting in GPU Queue...")

        # --- SMART FALLBACK SYSTEM ---
        # We try the 4 most common API names for Pinokio video scripts
        api_names_to_try = ["/generate_video", "/predict", "/generate", "/run"]
        result = None
        last_error = ""

        for name in api_names_to_try:
            try:
                status.write(f"🔄 Trying connection method: {name}...")
                result = client.predict(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_frames=duration * 8, 
                    aspect_ratio=aspect,
                    resolution=quality,
                    seed=-1,
                    api_name=name
                )
                if result: break # If it works, stop trying others
            except Exception as e:
                last_error = str(e)
                continue # Try the next name

        if result:
            status.update(label="✅ Video Ready!", state="complete", expanded=False)
            st.video(result)
            
            with open(result, "rb") as f:
                st.download_button(
                    label="📥 Download Video",
                    data=f,
                    file_name="velo_video.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        else:
            status.update(label="❌ Connection Failed", state="error")
            st.error("None of the standard API names worked.")
            st.info(f"Technical Error: {last_error}")

    except Exception as e:
        status.update(label="❌ Error", state="error")
        st.error(f"General Error: {e}")

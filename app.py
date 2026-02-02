import streamlit as st
from gradio_client import Client
import os

# --- 1. CONFIGURATION ---
# IMPORTANT: Update this link every time you restart Pinokio
FIXED_GRADIO_URL = "https://b2eca5eb64757141e9.gradio.live" 

st.set_page_config(page_title="Velo 1", page_icon="🎥", layout="centered")
st.title("🎥 Velo 1")
st.caption("AI Video Generation")

# --- 2. SMART SIDEBAR (LTX-2 LOGIC) ---
with st.sidebar:
    st.header("⚙️ Render Settings")
    
    # LTX-2 works best at these steps
    quality = st.select_slider("Resolution", options=["480p", "720p", "1080p"], value="720p")
    
    if quality == "1080p":
        st.warning("⚠️ 1080p locked to 9:16 and 10s to prevent H100's crashing. because of current model training")
        aspect = "9:16"
        duration = 10 # Seconds
    else:
        aspect = st.radio("Aspect Ratio", ["16:9", "9:16", "1:1"])
        duration = st.slider("Duration (Seconds)", 5, 15, 10)

    st.divider()
    st.info("Queue is active. Your request will process as soon as two of our GPU's is free.")

# --- 3. MAIN INTERFACE ---
prompt = st.text_area("Video Prompt:", "A cinematic shot of a red car driving through a forest, high detail, 4k", height=100)
negative_prompt = st.text_input("Negative Prompt (Optional):", "blurry, low quality, distorted")

generate_btn = st.button("Generate Video", type="primary", use_container_width=True)

if generate_btn:
    if not FIXED_GRADIO_URL or "your-link" in FIXED_GRADIO_URL:
        st.error("Owner must update the Gradio Link!")
        st.stop()

    status = st.status("🚀 Sending to Velo 1...", expanded=True)
    
    try:
        # Connect to your PC
        client = Client(FIXED_GRADIO_URL)
        
        # LTX-2 typically expects these inputs in this order.
        # If it fails, we use the 'api_name' trick.
        status.write("⏳ Waiting in GPU's Queue...")
        
        result = client.predict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            # We convert seconds to frames (LTX-2 usually runs at 24fps or 16fps)
            # Most Pinokio LTX-2 wrappers just take the raw number of seconds/frames
            num_frames=duration * 8, # Adjust multiplier based on your specific script
            aspect_ratio=aspect,
            resolution=quality,
            seed=-1, # -1 usually means random
            api_name="/predict" # If this fails, try "/generate"
        )
        
        status.update(label="✅ Video Ready!", state="complete", expanded=False)
        
        # Display Video
        st.video(result)
        
        # Download Button
        with open(result, "rb") as f:
            st.download_button(
                label="📥 Download Video",
                data=f,
                file_name="velo_video.mp4",
                mime="video/mp4",
                use_container_width=True
            )

    except Exception as e:
        status.update(label="❌ Connection Error", state="error")
        st.error(f"Error: {e}")
        st.info("Hint: Check if the 'api_name' in the code matches your Pinokio API (usually /predict or /generate)")


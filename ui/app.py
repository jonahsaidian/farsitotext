"""
Streamlit UI for Farsi Audio Transcriber.
"""
import streamlit as st
import tempfile
import os
import sys

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import transcribe_audio, get_default_api_key, validate_audio_file


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Farsi Transcriber",
        page_icon="🎵",
        layout="centered"
    )
    
    st.title("🎵 Farsi Transcriber")
    st.markdown("A simple tool to transcribe Farsi (Persian) audio to text via OpenAI.")
    
    # Initialize session state
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = ""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    
    # Step 1: API Key Input
    st.header("1. API Configuration")
    
    # Auto-populate API key from environment
    default_key = get_default_api_key()
    if default_key and not st.session_state.api_key:
        st.session_state.api_key = default_key
    
    api_key = st.text_input(
        "OpenAI API Key:",
        value=st.session_state.api_key,
        type="password",
        help="Enter your OpenAI API key. It will be auto-populated if set in environment variables."
    )
    
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ API key configured")
    else:
        st.warning("⚠️ Please enter your OpenAI API key")
        st.stop()
    
    # Step 2: File Selection
    st.header("2. Audio File Selection")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'],
        help="Supported formats: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ File selected: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / (1024*1024):.2f} MB")
        
        # Step 3: Transcribe Button
        st.header("3. Transcription")
        
        if st.button("🎯 Transcribe Audio", type="primary"):
            with st.spinner("Please wait as your audio file is processed..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Transcribe the audio
                    transcribed_text = transcribe_audio(tmp_file_path, api_key)
                    st.session_state.transcribed_text = transcribed_text
                    
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    
                    st.success("🎉 Your audio file has been transcribed!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.session_state.transcribed_text = ""
    else:
        st.info("📁 Please select an audio file to continue")
        st.stop()
    
    # Step 4: Display Results and Actions
    if st.session_state.transcribed_text:
        st.header("4. Transcription Results")
        
        # Display transcribed text
        st.text_area(
            "Transcribed Text:",
            value=st.session_state.transcribed_text,
            height=200,
            disabled=True
        )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download button
            st.download_button(
                label="💾 Save as Text File",
                data=st.session_state.transcribed_text,
                file_name="transcription.txt",
                mime="text/plain"
            )
        
        with col2:
            # Copy to clipboard button
            if st.button("📋 Copy to Clipboard"):
                st.write("Text copied! (Use Ctrl+V to paste)")
        
        with col3:
            # Start over button
            if st.button("🔄 Start Over"):
                # Reset session state
                st.session_state.transcribed_text = ""
                st.session_state.uploaded_file = None
                st.rerun()


if __name__ == "__main__":
    main()

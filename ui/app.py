"""
Streamlit UI for Farsi Audio Transcriber.
"""
import streamlit as st
import tempfile
import os
import sys
import time
import threading
from pydub import AudioSegment

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import transcribe_audio_segment, chunk_audio, get_default_api_key


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
            # Create progress bar and status
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Load audio file concurrently while updating an estimate (60s per 100MB, rounded to nearest 5s)
                file_mb = uploaded_file.size / (1024 * 1024)
                estimate_seconds = 60 * (file_mb / 100.0)
                rounded_seconds = int(round(estimate_seconds / 5.0) * 5)

                loaded_audio: dict = {"segment": None, "error": None}
                done_event = threading.Event()

                def _load_audio():
                    try:
                        seg = AudioSegment.from_file(tmp_file_path)
                        loaded_audio["segment"] = seg
                    except Exception as _e:
                        loaded_audio["error"] = str(_e)
                    finally:
                        done_event.set()

                threading.Thread(target=_load_audio, daemon=True).start()

                remaining = max(0, rounded_seconds)
                while not done_event.is_set() and remaining > 0:
                    status_text.text(f"Loading audio file... Estimated time: ~{remaining}s")
                    time.sleep(5)
                    remaining = max(0, remaining - 5)

                if not done_event.is_set():
                    status_text.text("Loading audio file... Estimated time: a few seconds remaining")

                # Ensure loading finished
                done_event.wait()
                if loaded_audio["error"]:
                    raise RuntimeError(f"Failed to load audio: {loaded_audio['error']}")
                audio = loaded_audio["segment"]
                
                # Chunk the audio
                status_text.text("Preparing audio for transcription...")
                chunked_audio = chunk_audio(audio, chunk_duration_ms=200000)
                
                # Transcribe each chunk with progress updates
                st.session_state.transcribed_text = ""  # Reset text
                total_chunks = len(chunked_audio)
                had_error = False
                
                for i, chunk in enumerate(chunked_audio):
                    remaining_chunks = max(0, total_chunks - (i + 1))
                    est_minutes = remaining_chunks  # ~1 minute per remaining chunk
                    est_label = f"~{est_minutes} min remaining" if est_minutes != 1 else "~1 min remaining"
                    status_text.text(f"Transcribing audio file: {est_label}")
                    progress_bar.progress((i + 1) / total_chunks)
                    
                    try:
                        chunk_text = transcribe_audio_segment(chunk, api_key)
                        if chunk_text.strip():
                            st.session_state.transcribed_text += chunk_text + " "
                    except Exception as e:
                        had_error = True
                        st.warning(f"Error transcribing chunk {i+1}: {e}")
                        continue
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
                # Decide final UI state based on success/error
                progress_bar.progress(1.0)
                if had_error or not st.session_state.transcribed_text.strip():
                    status_text.text("Sorry, we could not complete the transcription.")
                    st.error("Apologies — something went wrong transcribing your audio. Please try again.")
                    if st.button("🔄 Restart"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                else:
                    status_text.text("Transcription complete!")
                    st.success("🎉 Your audio file has been transcribed!")
                
            except Exception as e:
                st.error("Apologies — we couldn't transcribe your audio.")
                st.error(f"Details: {e}")
                if 'tmp_file_path' in locals():
                    try:
                        os.unlink(tmp_file_path)
                    except OSError:
                        pass
                if st.button("🔄 Restart"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
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
                # Fully reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


if __name__ == "__main__":
    main()

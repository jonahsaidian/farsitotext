"""
Streamlit UI for Farsi Audio Transcriber.
"""

import math
import os
import shutil
import sys
import tempfile

import streamlit as st

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import (
    chunk_audio,
    get_audio_duration_ms,
    get_default_api_key,
    postprocess_transcription,
    transcribe_audio_segment,
)


def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Farsi Transcriber", page_icon="🎵", layout="centered")
    st.title("🎵 Farsi Transcriber")
    st.markdown("A simple tool to transcribe Farsi (Persian) audio to text via OpenAI.")

    # Initialize session state
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = ""
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "uploaded_file" not in st.session_state:
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
        help="Enter your OpenAI API key. It will be auto-populated if set in environment variables.",
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
        type=["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"],
        help="Supported formats: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM",
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ File selected: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / (1024 * 1024):.2f} MB")

        # Step 3: Transcribe Button
        st.header("3. Transcription")

        if st.button("🎯 Transcribe Audio", type="primary"):
            st.session_state.had_error = False
            # Create progress bar and status
            progress_bar = st.progress(0)
            status_text = st.empty()
            result_box = st.empty()  # Placeholder for live transcription

            try:
                # Stream uploaded file to disk without loading into memory
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}"
                ) as tmp_file:
                    shutil.copyfileobj(uploaded_file, tmp_file)
                    tmp_file_path = tmp_file.name

                # Get duration via ffprobe for progress estimation
                status_text.text("Preparing audio for transcription...")
                chunk_duration_ms = 200000
                duration_ms = get_audio_duration_ms(tmp_file_path)
                total_chunks = math.ceil(duration_ms / chunk_duration_ms)
                chunked_audio = chunk_audio(tmp_file_path, chunk_duration_ms=chunk_duration_ms)

                # Transcribe each chunk with progress updates
                st.session_state.transcribed_text = ""  # Reset text

                # Show the result box as soon as transcription starts
                result_box.text_area(
                    "Transcribed Text (Live):",
                    value=st.session_state.transcribed_text,
                    height=200,
                    disabled=True,
                )
                for i, chunk_path in enumerate(chunked_audio):
                    remaining_chunks = max(0, total_chunks - (i + 1))
                    est_minutes = remaining_chunks // 3  # ~20 seconds per remaining chunk
                    est_label = (
                        f"~{est_minutes} min remaining" if est_minutes >= 1 else "~1 min remaining"
                    )
                    status_text.text(f"Transcribing audio file: {est_label}")
                    progress_bar.progress((i + 0.5) / total_chunks)

                    try:
                        chunk_text = transcribe_audio_segment(chunk_path, api_key)
                        if chunk_text.strip():
                            st.session_state.transcribed_text += chunk_text + " "
                            # Update the result box live
                            result_box.text_area(
                                "Transcribed Text (Live):",
                                value=st.session_state.transcribed_text,
                                height=200,
                                disabled=True,
                            )
                    except Exception as e:
                        st.session_state.had_error = True
                        st.error(f"Error transcribing chunk {i + 1}")
                        st.error(f"Details: {e}")
                        break
                    finally:
                        try:
                            os.unlink(chunk_path)
                        except OSError:
                            pass
                try:
                    # Post-process the fully transcribed text
                    st.session_state.transcribed_text = postprocess_transcription(
                        st.session_state.transcribed_text, api_key
                    )
                except Exception as e:
                    st.session_state.had_error = True
                    st.error("An error occurred during post-processing of the transcription.")
                    st.error(f"Details: {e}")
                # Clean up temporary file
                os.unlink(tmp_file_path)
                # Decide final UI state based on success/error
                progress_bar.progress(1.0)
                if st.session_state.had_error or not st.session_state.transcribed_text.strip():
                    if st.button("🔄 Restart"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.session_state.had_error = False
                        st.session_state.transcribed_text = ""
                        st.session_state.uploaded_file = None  # Clear the file uploader
                        st.rerun()
                else:
                    # Hide the live result box after transcription is complete
                    result_box.empty()
                    status_text.text("Transcription complete!")
                    st.success("🎉 Your audio file has been transcribed!")

            except Exception as e:
                st.session_state.had_error = True
                st.error("Apologies — we couldn't transcribe your audio.")
                st.error(f"Details: {e}")
                if "tmp_file_path" in locals():
                    try:
                        os.unlink(tmp_file_path)
                    except OSError:
                        pass
                if st.button("🔄 Restart"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.had_error = True
                    st.session_state.transcribed_text = ""
                    st.session_state.uploaded_file = None  # Clear the file uploader
                    st.rerun()
    else:
        st.info("📁 Please select an audio file to continue")

    # Step 4: Display Results and Actions
    if st.session_state.transcribed_text and not st.session_state.had_error:
        st.header("4. Transcription Results")

        # Display transcribed text
        st.text_area(
            "Transcribed Text:", value=st.session_state.transcribed_text, height=200, disabled=True
        )

        # Action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            # Download button
            st.download_button(
                label="💾 Save as Text File",
                data=st.session_state.transcribed_text,
                file_name="transcription.txt",
                mime="text/plain",
            )

        with col2:
            pass

        with col3:
            # Start over button
            if st.button("🔄 Start Over"):
                # Fully reset session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.uploaded_file = None  # Clear the file uploader
                st.rerun()


if __name__ == "__main__":
    main()

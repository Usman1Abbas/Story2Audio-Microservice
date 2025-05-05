import streamlit as st
import os
import httpx
import base64
from pathlib import Path
from typing import Optional

# Use environment variable for API URL if available, otherwise default to localhost
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="ASMR Conspiracy Generator",
    page_icon="🎧",
    layout="wide",
)

def generate_story(topic: str, max_tokens: int = 4000, temperature: float = 0.8) -> Optional[dict]:
    """Generate a story based on the topic."""
    with st.spinner("Generating story... This might take a minute or two."):
        try:
            with httpx.Client(timeout=300.0) as client:  # 5-minute timeout
                response = client.post(
                    f"{API_URL}/generate-story",
                    data={
                        "topic": topic,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            st.error(f"Error generating story: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None

def generate_audio(story_file: str) -> Optional[dict]:
    """Generate audio from a story file."""
    with st.spinner("Generating audio... This might take a minute."):
        try:
            with httpx.Client(timeout=300.0) as client:
                response = client.post(
                    f"{API_URL}/generate-audio",
                    data={"story_file": story_file}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            st.error(f"Error generating audio: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None

def generate_full(topic: str, max_tokens: int = 4000, temperature: float = 0.8) -> Optional[dict]:
    """Generate both a story and audio in one call."""
    with st.spinner("Generating story and audio... This might take a few minutes."):
        try:
            with httpx.Client(timeout=600.0) as client:  # 10-minute timeout
                response = client.post(
                    f"{API_URL}/generate",
                    data={
                        "topic": topic,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            st.error(f"Error generating content: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None

def display_audio_player(audio_path: str, file_format: str = "audio/mp3"):
    """Display an audio player for the generated audio."""
    try:
        if os.path.exists(audio_path):
            with open(audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            
            st.audio(audio_bytes, format=file_format)
            
            # Add download button
            file_name = os.path.basename(audio_path)
            st.download_button(
                label="Download Audio",
                data=audio_bytes,
                file_name=file_name,
                mime=file_format
            )
        else:
            st.error(f"Audio file not found at path: {audio_path}")
    except Exception as e:
        st.error(f"Error displaying audio: {e}")

def get_local_files():
    """Get lists of local story and audio files."""
    story_files = [f for f in os.listdir() if f.startswith("asmr_conspiracy_") and f.endswith(".txt")]
    audio_files = [f for f in os.listdir() if f.endswith("_audio.mp3")]
    
    return story_files, audio_files

def main():
    st.title("🎧 ASMR Conspiracy Generator")
    st.markdown("""
    Generate immersive ASMR conspiracy stories and audio narrations using AI.
    Enter a conspiracy topic and let the magic happen!
    """)
    
    st.divider()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Generate New", "Story to Audio", "Browse Files"])
    
    with tab1:
        st.subheader("Generate a New ASMR Conspiracy")
        
        with st.form("generate_form"):
            topic = st.text_input("Enter a conspiracy topic:", value="alien abductions")
            col1, col2 = st.columns(2)
            with col1:
                max_tokens = st.slider("Max story length:", 1000, 8000, 4000, 500)
            with col2:
                temperature = st.slider("Creativity level:", 0.1, 1.0, 0.8, 0.1)
            
            col1, col2 = st.columns(2)
            with col1:
                story_only = st.form_submit_button("Generate Story Only")
            with col2:
                full_generate = st.form_submit_button("Generate Story + Audio")
        
        if story_only:
            if not topic:
                st.error("Please enter a conspiracy topic.")
            else:
                result = generate_story(topic, max_tokens, temperature)
                if result and result.get("success", False):
                    st.success("Story generated successfully!")
                    with st.expander("Read the story", expanded=True):
                        st.markdown(result["story"])
                    
                    # Store the file path in the session state
                    if "story_file" not in st.session_state:
                        st.session_state.story_file = result["file_path"]
                    
                    # Add a button to generate audio later
                    if st.button("Generate Audio for this Story"):
                        audio_result = generate_audio(result["file_path"])
                        if audio_result and audio_result.get("success", False):
                            st.success("Audio generated successfully!")
                            display_audio_player(audio_result["audio_file_path"])
        
        if full_generate:
            if not topic:
                st.error("Please enter a conspiracy topic.")
            else:
                result = generate_full(topic, max_tokens, temperature)
                if result and result.get("success", False):
                    st.success("Story and audio generated successfully!")
                    
                    # Display the story
                    with st.expander("Read the story", expanded=True):
                        st.markdown(result["story"])
                    
                    # Display the audio
                    st.subheader("Listen to the narration")
                    display_audio_player(result["audio_file_path"])
    
    with tab2:
        st.subheader("Convert Existing Story to Audio")
        
        # Get existing story files
        story_files, _ = get_local_files()
        
        if not story_files:
            st.info("No story files found. Generate a story first.")
        else:
            selected_story = st.selectbox(
                "Select a story file to convert to audio:",
                story_files
            )
            
            if st.button("Generate Audio"):
                if selected_story:
                    audio_result = generate_audio(selected_story)
                    if audio_result and audio_result.get("success", False):
                        st.success("Audio generated successfully!")
                        display_audio_player(audio_result["audio_file_path"])
    
    with tab3:
        st.subheader("Browse Generated Files")
        
        # Get existing files
        story_files, audio_files = get_local_files()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Story Files")
            if not story_files:
                st.info("No story files found.")
            else:
                selected_story_file = st.selectbox("Select a story file to view:", story_files)
                if selected_story_file:
                    try:
                        with open(selected_story_file, "r", encoding="utf-8") as f:
                            story_content = f.read()
                        
                        st.markdown(story_content)
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
        
        with col2:
            st.write("### Audio Files")
            if not audio_files:
                st.info("No audio files found.")
            else:
                selected_audio_file = st.selectbox("Select an audio file to listen to:", audio_files)
                if selected_audio_file:
                    display_audio_player(selected_audio_file)

if __name__ == "__main__":
    main() 
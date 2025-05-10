

import os
import streamlit as st
import speech_recognition as sr
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Function to accept voice input
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening for voice input...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language="en-IN")  # Adjust for Hindi as needed
        return text  # ✅ Removed st.success() to avoid duplicate display
    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio.")
        return None
    except sr.RequestError:
        st.error("❌ Error with the speech recognition service.")
        return None

# YouTube search function
def search_youtube_videos(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    published_after = (datetime.now() - timedelta(days=14)).isoformat("T") + "Z"

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=25,
        publishedAfter=published_after,
        videoDuration="medium"  # Filters results to 4-20 minutes
    )
    response = request.execute()

    video_items = response.get("items", [])
    videos = []

    for item in video_items:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append((title, url))

    return videos

# Streamlit UI
st.set_page_config(page_title="YouTube Video Finder", page_icon="📺")
st.title("🔍 YouTube Video Finder")

# Option to choose between voice and text input
input_method = st.radio("Choose input method:", ["Text Input", "Voice Input"])

# Initialize query
query = ""

if input_method == "Text Input":
    query = st.text_input("Enter your search topic (Hindi/English):", "")
else:
    if st.button("🎙️ Start Voice Input"):
        voice_query = get_voice_input()
        if voice_query:
            st.session_state.query = voice_query
            st.session_state.voice_just_captured = True  # Flag that it was just captured
        else:
            st.warning("Voice input failed. Please try again.")

    query = st.session_state.get("query", "")
    if query and st.session_state.get("voice_just_captured"):
        st.success(f"✅ Voice Input Captured: {query}")
        st.session_state.voice_just_captured = False  # Reset flag

# Disable "Search" button unless we have a non-empty query
if st.button("🔎 Search"):
    if not query or not query.strip():
        st.warning("⚠️ Please enter or speak a search query.")
    else:
        with st.spinner("🔍 Searching YouTube..."):
            videos = search_youtube_videos(query)
            if not videos:
                st.error("😕 No videos found.")
            else:
                st.subheader("📄 Results:")
                for i, (title, url) in enumerate(videos, 1):
                    st.markdown(f"{i}. [{title}]({url})")




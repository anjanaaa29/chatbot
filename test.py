import streamlit
from streamlit_audiorecorder import audiorecorder
import streamlit as st

st.title("HR Q1: Why do you want this job?")

# Record
audio = audiorecorder("Click to record", "Click to stop")

# Playback
if audio:
    st.audio(audio.tobytes(), format="audio/wav")
    with open("hr_answer.wav", "wb") as f:
        f.write(audio.tobytes())

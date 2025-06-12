import streamlit as st
from audiorecorder import audiorecorder
from io import BytesIO
##############
from openai import OpenAI
from dotenv import dotenv_values, load_dotenv 
from my_package.api_key_loader_magic import configure_api_key, web_api, get_openai_client, api_magic
# Wczytaj dane z pliku .env
st.set_page_config(page_title="Audio Notatki", layout="wide")#layout="centered")
env = dotenv_values(".env")
api_magic()
##############

st.set_page_config(page_title="Audio Notatki", layout="centered")

st.title("Audio Notatki")
note_audio = audiorecorder(
    start_prompt="Nagraj notatkę",
    stop_prompt="Zatrzymaj nagrywanie",
)

# Debugowanie
if note_audio:
    st.success("Nagrywanie zakończone.")
    audio = BytesIO()
    note_audio.export(audio, format="mp3")
    note_audio_bytes = audio.getvalue()
    st.audio(note_audio_bytes, format="audio/mp3")
else:
    st.warning("Naciśnij przycisk, aby nagrać.")
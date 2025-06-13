from io import BytesIO
import streamlit as st
from audiorecorder import audiorecorder  # type: ignore
from dotenv import dotenv_values
from hashlib import md5
from openai import OpenAI

##############
from openai import OpenAI
from dotenv import dotenv_values, load_dotenv 
from my_package.api_key_loader_magic import configure_api_key, web_api, get_openai_client, api_magic
# Wczytaj dane z pliku .env
st.set_page_config(layout="wide")

env = dotenv_values(".env")
api_magic()     
##############

# env = dotenv_values(r"C:\Users\biela\Desktop\od_zera_do_ai\modul_7\gitek.env")

AUDIO_TRANSCRIBE_MODEL = "whisper-1"

@st.cache_resource
# def get_openai_client():
#     return OpenAI(api_key=env["OPENAI_API_KEY"])

def transcribe_audio(audio_bytes):
    openai_client = get_openai_client()
    audio_file = BytesIO(audio_bytes)
    audio_file.name = "audio.mp3"
    transcript = openai_client.audio.transcriptions.create(
        file=audio_file,
        model=AUDIO_TRANSCRIBE_MODEL,
        response_format="verbose_json",
    )

    return transcript.text

#
# MAIN
#

# st.set_page_config(page_title="Audio Notatki", layout="centered")

# Session state initialization
if "note_audio_bytes_md5" not in st.session_state:
    st.session_state["note_audio_bytes_md5"] = None

if "note_audio_bytes" not in st.session_state:
    st.session_state["note_audio_bytes"] = None

if "note_audio_text" not in st.session_state:
    st.session_state["note_audio_text"] = ""

st.title("Audio Notatki")
note_audio = audiorecorder(
    start_prompt="Nagraj notatkę",
    stop_prompt="Zatrzymaj nagrywanie",
)
if note_audio:
    audio = BytesIO()
    note_audio.export(audio, format="mp3")
    st.session_state["note_audio_bytes"] = audio.getvalue()

    current_md5 = md5(st.session_state["note_audio_bytes"]).hexdigest()
    if st.session_state["note_audio_bytes_md5"] != current_md5:
        st.session_state["note_audio_text"] = ""
        st.session_state["note_audio_bytes_md5"] = current_md5

    st.audio(st.session_state["note_audio_bytes"], format="audio/mp3")

    if st.button("Transkrybuj audio"):
        st.session_state["note_audio_text"] = transcribe_audio(st.session_state["note_audio_bytes"])

    if st.session_state["note_audio_text"]:
        st.text_area("Edytuj notatkę", value=st.session_state["note_audio_text"])
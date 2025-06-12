import json  # 0.25.0 bedzie mam potrzebny do zapisania pliku jako bazy danych
from pathlib import Path  # 025.1
import streamlit as st

# from streamlit_extras.bottom_container import bottom
# from streamlit_chat_widget import chat_input_widget

from openai import OpenAI
from dotenv import dotenv_values, load_dotenv # do czytania z plików .env
from my_package.api_key_loader import configure_api_key, web_api#, get_openai_client
from my_package.api_key_loader_magic import configure_api_key, web_api, get_openai_client, api_magic


import os
import requests# do pobrania kursu usd




import streamlit as st
from audiorecorder import audiorecorder
from io import BytesIO
st.set_page_config(page_title="Audio Notatki", layout="centered")
##############
from openai import OpenAI
from dotenv import dotenv_values, load_dotenv 
from my_package.api_key_loader_magic import configure_api_key, web_api, get_openai_client, api_magic
# Wczytaj dane z pliku .env
env = dotenv_values(".env")
api_magic()

web_api()

if 'OPENAI_API_KEY' not in st.secrets:
    configure_api_key(env)


# def get_openai_client():
#     return OpenAI(api_key=st.session_state["openai_api_key"])

############



st.title("Audio Notatki")
# note_audio = audiorecorder(
#     start_prompt="Nagraj notatkę",
#     stop_prompt="Zatrzymaj nagrywanie",
# )

# # Debugowanie
# if note_audio:
#     st.success("Nagrywanie zakończone.")
#     audio = BytesIO()
#     note_audio.export(audio, format="mp3")
#     note_audio_bytes = audio.getvalue()
#     st.audio(note_audio_bytes, format="audio/mp3")
# else:
#     st.warning("Naciśnij przycisk, aby nagrać.")
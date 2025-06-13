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

st.title("Audio Notatki")

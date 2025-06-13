
from io import BytesIO
import streamlit as st
from audiorecorder import audiorecorder  # type: ignore

from dotenv import dotenv_values
from hashlib import md5#V4 czy zmie niło nam się audio
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
# from my_package.api_key_loader_magic import configure_api_key, web_api, get_openai_client, api_magic
# st.set_page_config(layout="wide")
env = dotenv_values(".env")



### Secrets using Streamlit Cloud Mechanism
# https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
if 'QDRANT_URL' in st.secrets:
    env['QDRANT_URL'] = st.secrets['QDRANT_URL']
if 'QDRANT_API_KEY' in st.secrets:
    env['QDRANT_API_KEY'] = st.secrets['QDRANT_API_KEY']
###

EMBEDDING_MODEL = "text-embedding-3-large"#large/small
EMBEDDING_DIM = 3072#3072/1536
AUDIO_TRANSCRIBE_MODEL = "whisper-1"
QDRANT_COLLECTION_NAME = "notes"

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])

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

@st.cache_resource
def get_qdrant_client():
    return QdrantClient(
    url=env["QDRANT_URL"], 
    api_key=env["QDRANT_API_KEY"],
)
def assure_db_collection_exists():
    qdrant_client = get_qdrant_client()
    if not qdrant_client.collection_exists(QDRANT_COLLECTION_NAME):
        print("Tworzę kolekcję")
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
    else:
        print("Kolekcja już istnieje")

def get_embedding(text):
    openai_client = get_openai_client()
    result = openai_client.embeddings.create(input=[text], model=EMBEDDING_MODEL, dimensions=EMBEDDING_DIM)
    return result.data[0].embedding

def add_note_to_db(note_text):
    qdrant_client = get_qdrant_client()
    points_count = qdrant_client.count(collection_name=QDRANT_COLLECTION_NAME, exact=True)
    qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=points_count.count + 1,
                vector=get_embedding(text=note_text),
                payload={"text": note_text},
            )
        ]
    )

def list_notes_from_db(query=None):
    qdrant_client = get_qdrant_client()
    if not query:
        #daj mi pierwsze 40 elementów
        notes = qdrant_client.scroll(collection_name=QDRANT_COLLECTION_NAME, limit=40)[0]
        result = []
        for note in notes:
            result.append({
                "text": note.payload["text"],
                "score": None,
            })

        return result

    else:
        notes = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=get_embedding(text=query),
            limit=10,
        )
        result = []
        for note in notes:
            result.append({
                "text": note.payload["text"],
                "score": note.score,
            })

        return result

#
# MAIN
#    
#st.title("Audio Notatki AI")#TYTUŁ

st.set_page_config(page_title="Audio!Notatki", layout="centered")
# OpenAI API key protection
if not st.session_state.get("openai_api_key"):
    if "OPENAI_API_KEY" in env:
        st.session_state["openai_api_key"] = env["OPENAI_API_KEY"]

    else:
        st.info("Dodaj swój klucz API OpenAI aby móc korzystać z tej aplikacji")
        st.session_state["openai_api_key"] = st.text_input("Klucz API", type="password")
        if st.session_state["openai_api_key"]:
            st.rerun()

if not st.session_state.get("openai_api_key"):
    st.stop()

# Inicjalizacja st.session_state
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = None

if "note_audio_bytes_md5" not in st.session_state:#V4 czy zmie niło nam się audio
    st.session_state["note_audio_bytes_md5"] = None#V4 czy zmie niło nam się audio

if "note_audio_bytes" not in st.session_state:
    st.session_state["note_audio_bytes"] = None

if "note_text" not in st.session_state:
    st.session_state["note_text"] = ""

if "note_audio_text" not in st.session_state:
    st.session_state["note_audio_text"] = ""



st.title("Audio Notatki AI")
assure_db_collection_exists()

# Tworzenie zakładek
add_tab, upload_tab, search_tab = st.tabs(["Dodaj notatkę", "Wczytaj nagranie mp3", "Wyszukaj notatkę"])

# Zakładka: Dodaj notatkę

    # v1 - nagrywanie i odtwarzanie głosu.
with add_tab:
    note_audio = audiorecorder(start_prompt="Nagraj notatkę", stop_prompt="Zatrzymaj nagrywanie")

    if note_audio:
        audio = BytesIO()
        note_audio.export(audio, format="mp3")
        # note_audio_bytes = audio.getvalue()
        st.session_state["note_audio_bytes"] = audio.getvalue()

        current_md5 = md5(st.session_state["note_audio_bytes"]).hexdigest()#V4 przekaże bity audio do md5
        if st.session_state["note_audio_bytes_md5"] != current_md5:#V4 czy zczy nie jest równe i się zmieniło
            st.session_state["note_audio_text"] = ""#V4 resetujemy
            st.session_state["note_text"] = ""#v5
            st.session_state["note_audio_bytes_md5"] = current_md5#V4 zapisujemy na nową wartość

        st.audio(st.session_state["note_audio_bytes"], format="audio/mp3")

        if st.button("Transkrybuj nagrane audio", key="transcribe_recorded"):
            st.session_state["note_audio_text"] = transcribe_audio(st.session_state["note_audio_bytes"])

        if st.session_state["note_audio_text"]:
            st.session_state["note_text"] = st.text_area("Edytuj notatkę", value=st.session_state["note_audio_text"])

        if st.session_state["note_text"] and st.button("Wyślij notatkę do twórcy aplikacji", disabled=not st.session_state["note_text"], key="save_note"):
            
            add_note_to_db(note_text=st.session_state["note_text"])
            st.toast("Notatka zapisana", icon="🎉")

    # Przyciski do zapisu plików
    if st.session_state["note_audio_bytes"]:
        if st.button("Zapisz MP3 na dysku", key="save_mp3"):
            st.download_button("Pobierz MP3", st.session_state["note_audio_bytes"], "audio.mp3")

    if st.session_state["note_audio_text"]:
        if st.button("Zapisz TXT na dysku", key="save_txt"):
            st.download_button("Pobierz TXT", st.session_state["note_audio_text"], "note.txt", key="download_recorded_txt_button")

# Zakładka: Wczytaj nagranie mp3
with upload_tab:
    uploaded_file = st.file_uploader("Wczytaj notatkę MP3", type=["mp3"])
    if uploaded_file is not None:
        st.session_state["note_audio_bytes"] = uploaded_file.read()
        st.audio(st.session_state["note_audio_bytes"], format="audio/mp3")

        if st.button("Transkrybuj wczytane audio", key="transcribe_uploaded"):
            st.session_state["note_audio_2text"] = transcribe_audio(st.session_state["note_audio_bytes"])

        if "note_audio_2text" in st.session_state and st.session_state["note_audio_2text"]:
            st.session_state["note_2text"] = st.text_area("Edytuj notatkę", value=st.session_state["note_audio_2text"])

    # Przyciski do zapisu plików
    if "note_audio_2text" in st.session_state and st.session_state["note_audio_2text"]:
        if st.button("Zapisz TXT", key="download_uploaded_txt"):
            st.download_button("Pobierz TXT", st.session_state["note_audio_2text"], "notatka.txt", key="download_uploaded_txt_button")

# Zakładka: Szukaj notatkę
with search_tab:
    query = st.text_input("Wyszukaj notatkę")
    if st.button("Szukaj", key="search_note"):
        notes = list_notes_from_db(query)
        for note in notes:
            with st.container(border=True):
                st.markdown(note["text"])
                if note["score"]:
                    st.markdown(f':violet[{note["score"]}]')

import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values, load_dotenv # do czytania z plików .env

# # !!!należy wywołać w głównym  poniższe importy i 2 wiersze uruchamiające!!!
# from openai import OpenAI
# from dotenv import dotenv_values, load_dotenv 
# from my_package.api_key_loader_magic import configure_api_key, web_api, get_openai_client, api_magic
# # Wczytaj dane z pliku .env
# env = dotenv_values(".env")
# api_magic()




env = dotenv_values(".env")
#wywołanie
# from my_package.api_key_loader import configure_api_key
# configure_api_key(env)

#
# def get_openai_client():
#     return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# def get_openai_client():
#     return OpenAI(api_key=st.session_state["openai_api_key"])
def web_api():
    if 'OPENAI_API_KEY' in st.secrets:
        st.session_state["openai_api_key"] = st.secrets['OPENAI_API_KEY']
        env['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']


def configure_api_key(env):
    with st.sidebar:
        col1, col2 = st.columns([9, 4])
        with col1:
            with st.expander(f"Wczytaj API_key"):
                tab1, tab2, tab3 = st.tabs(["Lokal", "Upload_API_KEY", "WEB"])

                # Opcja 1: Klucz z pliku .env
                with tab1:
                    if st.button("env_w_katalogu_aplikacji_VSCODE"):
                        st.info("env w katalogu aplikacji uruchamiany na VSCODE")
                        if 'openai_api_key' in env:
                            st.session_state["openai_api_key"] = env['openai_api_key']
                        elif st.session_state.get("openai_api_key"):
                            st.success("Klucz API został zapisany do sesji na twoim komputerze.")
                        else:
                            st.info("Nie znaleziono klucza API OpenAI. Ustaw go w pliku .env lub wpisz manualnie.")

                # Opcja 2: Klucz z pliku
                with tab2:
                    uploaded_file = st.file_uploader("Wczytaj plik z kluczami API dla modułów LLM", type=None)
                    st.info("znajduje klucz z pliku zapisanego w formie .env czyli: OPENAI_API_KEY=********")
                    if uploaded_file is not None:
                        content = uploaded_file.read().decode('utf-8')
                        lines = content.splitlines()

                        # Funkcja do wyszukiwania klucza
                        def find_key(lines, prefix):
                            for line in lines:
                                if line.strip().startswith(prefix):
                                    return line.strip().replace(prefix, "").strip()
                            return None

                        openai_key = find_key(lines, "OPENAI_API_KEY=")

                        if openai_key:
                            st.write("Klucz OpenAI API znaleziono")
                            st.session_state["openai_api_key"] = openai_key
                            st.success("Klucz API został zapisany do sesji na twoim komputerze.")
                        else:
                            st.write("Nie znaleziono klucza OpenAI API w pliku.")

                # Opcja 3: Klucz ze streamlit Secrets
                with tab3:
                    if st.button("streamlit_Secrets"):
                        if 'OPENAI_API_KEY' in st.secrets:
                            st.session_state["openai_api_key"] = st.secrets['OPENAI_API_KEY']
                            env['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
                        elif st.session_state.get("openai_api_key"):
                            st.success("Klucz API już jest w sesji")
                        else:
                            st.error("Nie znaleziono klucza API OpenAI. Ustaw go w streamlit > App settings > Secrets.")

        # with col2:
        #     if st.button("WEB_API"):
        #         if 'OPENAI_API_KEY' in st.secrets:
        #             st.session_state["openai_api_key"] = st.secrets['OPENAI_API_KEY']
        #             env['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

    # Ochrona klucza API
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

#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv!!!!!!!!!!!!!!!!!!!!!!!!
def api_magic():
    web_api()

    if 'OPENAI_API_KEY' not in st.secrets:
        configure_api_key(env)

    # def get_openai_client():
    #     return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_openai_client():
    return OpenAI(api_key=st.session_state["openai_api_key"])

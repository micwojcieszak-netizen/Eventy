import streamlit as st
import pandas as pd

# Konfiguracja strony
st.set_page_config(page_title="MPKTech IDStore - Space Dashboard", layout="wide")

# Stylizacja "Space" za pomocą CSS
st.markdown("""
    <style>
    .main {
        background-color: #0b0d17;
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #4b0082;
        color: white;
        border-radius: 10px;
    }
    .stTextInput>div>div>input {
        background-color: #1a1c2c;
        color: #00d4ff;
    }
    h1, h2, h3 {
        color: #8a2be2;
        text-shadow: 2px 2px #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicjalizacja danych w sesji (jeśli nie istnieją)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"ID": "ZF682", "Store": "Zabka-pl-ost-1", "Name": "Ostróda Yachts", "Adres": "Ostróda, ul. Spokojna 1", "Status": "Active", "Komentarze": ""}
    ])

st.title("🚀 Zabka MPKTech IDStore")

# --- SEKCJA WYŚWIETLANIA ---
st.subheader("🛰️ Aktywne Lokalizacje")
st.table(st.session_state.data)

# --- SEKCJA KOMENTARZY (Dostępna dla wszystkich) ---
st.divider()
st.subheader("💬 Dodaj komentarz")
selected_id = st.selectbox("Wybierz ID punktu", st.session_state.data["ID"])
new_comment = st.text_input("Treść komentarza")
if st.button("Wyślij komentarz"):
    idx = st.session_state.data.index[st.session_state.data['ID'] == selected_id][0]
    old_comm = st.session_state.data.at[idx, "Komentarze"]
    st.session_state.data.at[idx, "Komentarze"] = f"{old_comm} | {new_comment}" if old_comm else new_comment
    st.success("Komentarz dodany!")
    st.rerun()

# --- SEKCJA ADMINA (Chroniona hasłem) ---
st.sidebar.title("🔐 Panel Administratora")
password = st.sidebar.text_input("Wprowadź hasło", type="password")

if password == "Aifi-2026":
    st.sidebar.success("Zalogowano")
    st.divider()
    st.header("🛠️ Zarządzanie Bazą")
    
    tab1, tab2, tab3 = st.tabs(["➕ Dodaj", "❌ Usuń", "🔄 Zmień Status"])
    
    with tab1:
        with st.form("add_form"):
            new_id = st.text_input("ID")
            new_store = st.text_input("Store")
            new_name = st.text_input("Name")
            new_adr = st.text_input("Adres")
            new_stat = st.selectbox("Status", ["Active", "Inactive", "Maintenance"])
            if st.form_submit_button("Dodaj punkt"):
                new_row = {"ID": new_id, "Store": new_store, "Name": new_name, "Adres": new_adr, "Status": new_stat, "Komentarze": ""}
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

    with tab2:
        del_id = st.selectbox("Wybierz ID do usunięcia", st.session_state.data["ID"], key="del")
        if st.button("Usuń trwale"):
            st.session_state.data = st.session_state.data[st.session_state.data["ID"] != del_id]
            st.rerun()

    with tab3:
        edit_id = st.selectbox("Zmień status dla ID", st.session_state.data["ID"], key="edit")
        next_status = st.selectbox("Nowy status", ["Active", "Inactive", "Maintenance"], key="stat_edit")
        if st.button("Aktualizuj status"):
            idx = st.session_state.data.index[st.session_state.data['ID'] == edit_id][0]
            st.session_state.data.at[idx, "Status"] = next_status
            st.rerun()
else:
    if password:
        st.sidebar.error("Błędne hasło")

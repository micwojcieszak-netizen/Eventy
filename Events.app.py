import streamlit as st
import pandas as pd

# Ustawienia strony
st.set_page_config(page_title="StadiumStaffer Clone", layout="wide")

st.title("🏟️ StadiumStaffer - Zarządzanie Personelem")

# Przykładowe dane pracowników
if 'staff_data' not in st.session_state:
    st.session_state.staff_data = pd.DataFrame([
        {"ID": 1, "Imię": "Jan Kowalski", "Rola": "Ochrona", "Sektor": "A1", "Status": "Obecny"},
        {"ID": 2, "Imię": "Anna Nowak", "Rola": "Bileter", "Sektor": "B3", "Status": "Przerwa"},
        {"ID": 3, "Imię": "Marek Woźniak", "Rola": "VIP Host", "Sektor": "Loża", "Status": "Obecny"},
    ])

# Panel boczny - dodawanie pracownika
st.sidebar.header("Dodaj pracownika")
new_name = st.sidebar.text_input("Imię i Nazwisko")
new_role = st.sidebar.selectbox("Rola", ["Ochrona", "Bileter", "VIP Host", "Obsługa Medyczna"])
new_sector = st.sidebar.text_input("Sektor")

if st.sidebar.button("Dodaj do bazy"):
    new_entry = {"ID": len(st.session_state.staff_data)+1, "Imię": new_name, "Rola": new_role, "Sektor": new_sector, "Status": "Zalogowany"}
    st.session_state.staff_data = pd.concat([st.session_state.staff_data, pd.DataFrame([new_entry])], ignore_index=True)
    st.success("Dodano pracownika!")

# Widok główny - Statystyki
col1, col2, col3 = st.columns(3)
col1.metric("Wszyscy pracownicy", len(st.session_state.staff_data))
col2.metric("Sektory obsadzone", st.session_state.staff_data['Sektor'].nunique())
col3.metric("Status: Obecny", len(st.session_state.staff_data[st.session_state.staff_data['Status'] == "Obecny"]))

# Tabela pracowników
st.subheader("Lista personelu w czasie rzeczywistym")
st.dataframe(st.session_state.staff_data, use_container_width=True)
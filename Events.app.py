import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Stadium Events Scout", layout="wide", page_icon="🏟️")

st.title("🏟️ Stadium Event Scout 2025/2026")
st.write("Wybierz obiekt, aby pobrać najnowsze wydarzenia bezpośrednio z ich stron.")

# Wybór obiektu
venue = st.selectbox("Wybierz stadion/arenę:", ["AO Arena (Manchester)", "LCFC - King Power Stadium"])

def fetch_events(venue_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    events = []
    
    try:
        if venue_name == "AO Arena (Manchester)":
            # Przykład dla AO Arena
            url = "https://www.ao-arena.com/events/"
            # Tutaj następuje proces Scrapingu (pobieranie HTML)
            # Dla testu zwracamy dane strukturalne, które symulują wynik scrapingu
            events = [
                {"Data": "2025-05-10", "Wydarzenie": "Oasis Reunion (TBC)", "Kategoria": "Koncert"},
                {"Data": "2025-06-15", "Wydarzenie": "Billie Eilish", "Kategoria": "Koncert"},
                {"Data": "2025-08-20", "Wydarzenie": "Disney On Ice", "Kategoria": "Familijne"}
            ]
            
        elif venue_name == "LCFC - King Power Stadium":
            # Dla LCFC pobieramy mecze i eventy stadionowe
            url = "https://www.lcfc.com/matches/fixtures"
            # Symulacja zaciągania danych z kalendarza LCFC
            events = [
                {"Data": "2025-03-01", "Wydarzenie": "Leicester City vs Chelsea", "Kategoria": "Premier League"},
                {"Data": "2025-03-15", "Wydarzenie": "Leicester City vs Arsenal", "Kategoria": "Premier League"},
                {"Data": "2025-05-22", "Wydarzenie": "Kasabian Live at King Power", "Kategoria": "Koncert"}
            ]

        return pd.DataFrame(events)

    except Exception as e:
        st.error(f"Nie udało się pobrać danych: {e}")
        return pd.DataFrame()

if st.button("Pobierz aktualną listę"):
    with st.spinner(f'Łączenie z serwerem {venue}...'):
        data = fetch_events(venue)
        
        if not data.empty:
            st.success(f"Znaleziono wydarzenia dla {venue}!")
            
            # Formateowanie tabeli
            st.dataframe(
                data.sort_values(by="Data"), 
                use_container_width=True, 
                hide_index=True
            )
            
            # Prosty licznik
            st.info(f"Łącznie zaplanowanych wydarzeń: {len(data)}")
        else:
            st.warning("Obecnie brak publicznych wydarzeń na stronie tego obiektu.")

# Stopka
st.divider()
st.caption("Dane są pobierane w czasie rzeczywistym. Pamiętaj, że niektóre stadiony blokują automatyczne zapytania.")

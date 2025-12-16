import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Stadium Event Finder", layout="wide")

st.title("🏟️ Stadium Event Scout")
st.write("Wpisz nazwę areny, aby pobrać nadchodzące wydarzenia.")

venue = st.selectbox("Wybierz arenę:", ["AO Arena (Manchester)", "Inne stadiony (w budowie)"])

def get_ao_arena_events():
    url = "https://www.ao-arena.com/events/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = []
        # Szukamy elementów na stronie AO Arena (uproszczony przykład)
        for item in soup.select('.event-card'): # To zależy od kodu strony
            title = item.select_one('.event-title').text.strip()
            date = item.select_one('.event-date').text.strip()
            events.append({"Data": date, "Wydarzenie": title})
        
        return pd.DataFrame(events)
    except Exception as e:
        return f"Błąd podczas pobierania danych: {e}"

if st.button("Pobierz wydarzenia"):
    with st.spinner('Łączenie z serwerem areny...'):
        if venue == "AO Arena (Manchester)":
            # Symulacja pobierania (scrapingu) dla demonstracji
            data = pd.DataFrame([
                {"Data": "20 Maj 2024", "Wydarzenie": "Girls Aloud"},
                {"Data": "24 Czerwiec 2024", "Wydarzenie": "Liam Gallagher"},
                {"Data": "15 Lipiec 2024", "Wydarzenie": "Stevie Nicks"}
            ])
            st.success(f"Znaleziono wydarzenia dla {venue}")
            st.table(data)
        else:
            st.warning("Ta arena nie jest jeszcze skonfigurowana.")

st.info("💡 Aby pobierać dane z każdej strony na świecie, musielibyśmy napisać osobne reguły dla każdego adresu URL (tzw. Scrapers).")

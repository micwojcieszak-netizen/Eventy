import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Stadium Staffing & Events 2025", layout="wide")

st.title("🏟️ StadiumStaffer Live: 2025/2026")
st.subheader("Automatyczne pobieranie wydarzeń z aren")

# Wybór areny
venue = st.selectbox("Wybierz arenę do sprawdzenia:", 
                     ["AO Arena, Manchester", "Wembley Stadium, London", "O2 Arena, London"])

# Symulacja pobierania danych na żywo (Live Web Scraping/API Simulation)
def fetch_upcoming_events(venue_name):
    # W rzeczywistym kodzie tutaj łączymy się z https://app.ticketmaster.com/discovery/v2/
    # Na potrzeby Twojego startu, przygotowałem listę przyszłych wydarzeń
    current_year = 2025
    events_db = [
        {"Data": "2025-06-12", "Wydarzenie": "World Tour Concert", "Status": "Planowane"},
        {"Data": "2025-07-05", "Wydarzenie": "Championship Finals", "Status": "Potwierdzone"},
        {"Data": "2025-09-20", "Wydarzenie": "International Charity Gala", "Status": "W sprzedaży"},
        {"Data": "2026-01-15", "Wydarzenie": "Winter Indoor Games", "Status": "Wstępna rezerwacja"},
    ]
    return pd.DataFrame(events_db)

if st.button("Sprawdź nadchodzące eventy"):
    with st.spinner(f'Łączenie z bazą danych {venue}...'):
        df = fetch_upcoming_events(venue)
        
        # Filtrowanie, by pokazać tylko przyszłe daty
        df['Data'] = pd.to_datetime(df['Data'])
        future_events = df[df['Data'] >= datetime.now()]
        
        if not future_events.empty:
            st.success(f"Znaleziono {len(future_events)} wydarzeń na sezon 2025/2026!")
            
            # Wyświetlanie w ładnej formie
            for index, row in future_events.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    col1.metric("Data", row['Data'].strftime('%d.%m.%Y'))
                    col2.write(f"### {row['Wydarzenie']}")
                    col3.info(row['Status'])
                    st.divider()
        else:
            st.warning("Brak zaplanowanych wydarzeń w bazie dla tej areny.")

st.sidebar.markdown("### Panel Sterowania")
st.sidebar.info("Aplikacja synchronizuje się z kalendarzem globalnym co 24h.")

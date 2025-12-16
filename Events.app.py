import streamlit as st
from serpapi import GoogleSearch
from datetime import datetime
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="StadiumStaffer Clone", layout="wide")

# Stylizacja CSS dla kart (identyczna jak na zdjęciu)
st.markdown("""
    <style>
    .event-card {
        background-color: #fff9f2; /* Jasnopomarańczowe tło jak na screenie */
        border: 1px solid #ffe8cc;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        color: #1a1a1a;
    }
    .status-badge {
        background-color: #fff4e6;
        color: #d9480f;
        padding: 5px 12px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .event-title { font-weight: bold; font-size: 1.2rem; }
    .countdown { color: #d9480f; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_content_html=True)

st.title("Schedule Overview")
st.write("Wyszukaj nadchodzące wydarzenia dla dowolnej drużyny lub areny.")

# --- WYSZUKIWARKA ---
query = st.text_input("Wpisz nazwę (np. LCFC, AO Arena, Manchester City):", "LCFC")

def fetch_live_events(search_query):
    params = {
        "q": f"{search_query} events schedule",
        "hl": "en",
        "gl": "gb",
        "api_key": "TWÓJ_KLUCZ_SERPAPI" # <--- WKLEJ TUTAJ SWÓJ KLUCZ
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    events = []
    
    # Przeszukiwanie wyników "Knowledge Graph" (Google Events)
    if "events_results" in results:
        for ev in results["events_results"]:
            title = ev.get("title")
            venue = ev.get("venue", {}).get("name", "Unknown Venue")
            # Próba wyciągnięcia daty
            date_raw = ev.get("date", {}).get("start_time", "2025-12-25 15:00")
            
            events.append({
                "title": title,
                "venue": venue,
                "date": date_raw,
                "status": "Upcoming"
            })
    return events

# --- WYŚWIETLANIE ---
if query:
    data = fetch_live_events(query)
    
    if data:
        st.subheader(f"Upcoming Schedule for: {query}")
        cols = st.columns(2)
        
        for i, ev in enumerate(data):
            with cols[i % 2]:
                # Obliczanie dni do wydarzenia (uproszczone)
                try:
                    event_dt = pd.to_datetime(ev['date'])
                    days_left = (event_dt.replace(tzinfo=None) - datetime.now()).days
                except:
                    days_left = "?"

                st.markdown(f"""
                    <div class="event-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div class="event-title">{ev['title']}</div>
                            <div class="status-badge">⚠️ {ev['status']}</div>
                        </div>
                        <div style="color: #666; margin-top: 5px;">{ev['venue']}</div>
                        <div style="margin-top: 10px;">🕒 {ev['date']}</div>
                        <div class="countdown">Happening in {days_left} days</div>
                    </div>
                """, unsafe_content_html=True)
    else:
        st.warning("Nie znaleziono oficjalnych wydarzeń. Spróbuj dopisać nazwę miasta.")

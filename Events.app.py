import streamlit as st
from serpapi import GoogleSearch
import pandas as pd

# 1. KONFIGURACJA STRONY - MUSI BYĆ PIERWSZA
st.set_page_config(page_title="StadiumStaffer Dashboard", layout="wide")

# 2. DEFINICJA STYLU JAKO ZMIENNA TEKSTOWA (To zapobiega błędowi TypeError)
css_style = """
<style>
    [data-testid="stAppViewContainer"] { background-color: #fcfcfc; }
    .event-card {
        background-color: #fff9f2; 
        border: 1px solid #ffe8cc;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .status-badge {
        background-color: #fff4e6;
        color: #d9480f;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
        float: right;
        font-size: 0.8rem;
    }
    .event-title { font-weight: bold; font-size: 1.1rem; color: #1a1a1a; }
    .event-venue { color: #666; font-size: 0.9rem; margin-bottom: 10px; }
    .countdown { color: #d9480f; font-weight: bold; margin-top: 8px; font-size: 0.9rem; }
</style>
"""

# Wstrzyknięcie stylu
st.markdown(css_style, unsafe_content_html=True)

# 3. NAGŁÓWEK I WYSZUKIWARKA
st.title("Schedule Overview")
st.write("Upcoming events across all venues in the next 14 days.")

query = st.text_input("Enter Venue or Team (e.g. LCFC, Wembley):", "LCFC")

# 4. FUNKCJA POBIERAJĄCA DANE (SerpApi)
def get_events(search_term):
    # TWÓJ KLUCZ API
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f" 
    
    params = {
        "q": f"{search_term} fixtures events schedule",
        "hl": "en",
        "gl": "gb",
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        events_list = []
        
        # Przeszukiwanie wyników sportowych (mecze)
        if "sports_results" in results and "games" in results["sports_results"]:
            for game in results["sports_results"]["games"][:6]:
                teams = game.get("teams", [{},{}])
                t1 = teams[0].get("name", "TBD")
                t2 = teams[1].get("name", "TBD")
                events_list.append({
                    "title": f"{t1} v {t2}",
                    "venue": search_term.upper(),
                    "date": game.get("date", "Upcoming"),
                    "status": "Upcoming"
                })
        
        # Przeszukiwanie kalendarza wydarzeń (koncerty)
        if not events_list and "events_results" in results:
            for ev in results["events_results"][:6]:
                events_list.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term.upper()),
                    "date": ev.get("date", {}).get("when", "Upcoming"),
                    "status": "Scheduled"
                })
        
        return events_list
    except:
        return []

# 5. GENEROWANIE WIDOKU
data = get_events(query)

# Liczniki
c1, c2 = st.columns(2)
c1.metric("UPCOMING (TOTAL)", len(data))
c2.metric("TRACKED SEARCH", query.upper())

st.markdown("### 🗓️ Upcoming Schedule")

if data:
    # Rysowanie kart w dwóch kolumnach
    cols = st.columns(2)
    for i, ev in enumerate(data):
        with cols[i % 2]:
            # Budowanie karty HTML jako jeden ciąg znaków (bezpieczniej dla Pythona 3.13)
            card = f'<div class="event-card">'
            card += f'<span class="status-badge">⚠️ {ev["status"]}</span>'
            card += f'<div class="event-title">{ev["title"]}</div>'
            card += f'<div class="event-venue">{ev["venue"]}</div>'
            card += f'<div style="color: #444; font-size: 0.9rem;">🕒 {ev["date"]}</div>'
            card += f'<div class="countdown">Data synchronized live</div>'
            card += f'</div>'
            st.markdown(card, unsafe_content_html=True)
else:
    st.info("No events found. Check your search query.")

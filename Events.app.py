import streamlit as st
from serpapi import GoogleSearch
from datetime import datetime
import pandas as pd

# 1. KONFIGURACJA STRONY
st.set_page_config(page_title="StadiumStaffer Dashboard", layout="wide")

# 2. STYLIZACJA CSS (Zgodna z Twoim zdjęciem)
st.markdown("""
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
""", unsafe_content_html=True)

# 3. NAGŁÓWEK
st.title("Schedule Overview")
st.write("Upcoming events across all venues in the next 14 days.")

# Wyszukiwarka
query = st.text_input("Enter Venue or Team (np. LCFC, AO Arena, Wembley):", "LCFC")

# 4. FUNKCJA POBIERAJĄCA DANE LIVE (SerpApi)
def get_events(search_term):
    # Twój klucz API został dodany poniżej
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
        
        # 1. Przeszukiwanie wyników sportowych (mecze)
        if "sports_results" in results and "games" in results["sports_results"]:
            for game in results["sports_results"]["games"][:8]:
                teams = game.get("teams", [{},{}])
                t1 = teams[0].get("name", "TBD")
                t2 = teams[1].get("name", "TBD")
                events_list.append({
                    "title": f"{t1} v {t2}",
                    "venue": search_term.upper(),
                    "date": game.get("date", "Upcoming"),
                    "status": "Upcoming"
                })
        
        # 2. Przeszukiwanie kalendarza wydarzeń (koncerty/arenia)
        if not events_list and "events_results" in results:
            for ev in results["events_results"][:8]:
                events_list.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term.upper()),
                    "date": ev.get("date", {}).get("when", "Upcoming"),
                    "status": "Scheduled"
                })
        
        return events_list
    except Exception as e:
        return []

# 5. LOGIKA WYŚWIETLANIA I STATYSTYKI
data = get_events(query)

# Górne liczniki
c1, c2 = st.columns(2)
c1.metric("UPCOMING (TOTAL)", len(data))
c2.metric("TRACKED SEARCH", query.upper())

st.markdown("### 🗓️ Upcoming Schedule")

# Generowanie kart w 2 kolumnach (identycznie jak na screenie)
if data:
    cols = st.columns(2)
    for i, ev in enumerate(data):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="event-card">
                    <span class="status-badge">⚠️ {ev['status']}</span>
                    <div class="event-title">{ev['title']}</div>
                    <div class="event-venue">{ev['venue']}</div>
                    <div style="color: #444; font-size: 0.9rem;">🕒 {ev['date']}</div>
                    <div class="countdown">Data synchronized live via Google</div>
                </div>
            """, unsafe_content_html=True)
else:
    st.info("No events found. Try searching for something else (e.g. 'Manchester City' or 'O2 Arena').")

if st.button("🔄 Refresh Data"):
    st.rerun()

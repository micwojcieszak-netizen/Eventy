import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random

# 1. KONFIGURACJA STRONY
st.set_page_config(page_title="Event Collector 💡", layout="wide")

# 2. DESIGN DARK MODE
st.html("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0b0d11; color: #ffffff; font-family: 'Inter', sans-serif; }
    .event-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 22px; margin-bottom: 20px; transition: 0.3s;
    }
    .event-card:hover { border-color: #00d4ff; background: rgba(255, 255, 255, 0.05); }
    .status-badge {
        background-color: rgba(0, 212, 255, 0.1); color: #00d4ff;
        padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.7rem; text-transform: uppercase;
    }
    .prediction-box {
        background: rgba(0, 212, 255, 0.07); border-radius: 12px; padding: 12px; margin-top: 15px;
    }
    .jira-btn {
        display: block; width: 100%; text-align: center; background: #0052cc;
        color: white !important; text-decoration: none; padding: 10px;
        border-radius: 8px; font-weight: bold; margin-top: 15px; font-size: 0.8rem;
    }
</style>
""")

st.markdown("# Event Collector 💡")
query = st.text_input("Wyszukaj stadion, miasto lub drużynę:", "AO Arena Manchester")

CAPACITIES = {
    "WEMBLEY": 90000, "AO ARENA": 21000, "LCFC": 32261, "KING POWER": 32261, 
    "O2 ARENA": 20000, "TAURON": 15000, "NARODOWY": 58000, "CAMP NOU": 99000,
    "MADISON SQUARE": 19500, "ANFIELD": 54000, "OLD TRAFFORD": 74000
}

def get_prediction(venue_name):
    venue_upper = venue_name.upper()
    capacity = 15000
    for key, val in CAPACITIES.items():
        if key in venue_upper:
            capacity = val
            break
    predicted = int(capacity * random.uniform(0.85, 0.98))
    return predicted, capacity

def get_live_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f" 
    params = {
        "q": f"{search_term} upcoming events schedule 2025 2026",
        "hl": "en",
        "gl": "gb",
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        events_list = []
        
        # 1. Szukaj w oficjalnych widgetach wydarzeń Google
        if "events_results" in results:
            for ev in results["events_results"][:12]:
                events_list.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term),
                    "date": ev.get("date", {}).get("when", "2025/2026"),
                    "type": "EVENT"
                })
        
        # 2. Szukaj w wynikach sportowych
        if "sports_results" in results and "games" in results["sports_results"]:
            for game in results["sports_results"]["games"][:8]:
                teams = game.get("teams", [{},{}])
                events_list.append({
                    "title": f"{teams[0].get('name', 'Team A')} vs {teams[1].get('name', 'Team B')}",
                    "venue": search_term.upper(),
                    "date": game.get("date", "Upcoming Match"),
                    "type": "MATCH"
                })

        # 3. KLUCZOWA POPRAWKA: Jeśli nie ma widgetów, wyciągnij nazwy z tytułów stron (Organic)
        if not events_list and "organic_results" in results:
            for res in results["organic_results"][:8]:
                title = res.get("title")
                # Czyścimy tytuł z nazwy strony (np. usuwamy "| Ticketmaster")
                clean_title = title.split('|')[0].split('-')[0].strip()
                
                snippet = res.get("snippet", "")
                
                events_list.append({
                    "title": clean_title,
                    "venue": search_term,
                    "date": "Check details in Jira",
                    "type": "DISCOVERED"
                })
                
        return events_list
    except Exception as e:
        return []

# WYŚWIETLANIE
data = get_live_data(query)

if data:
    st.metric("TOTAL EVENTS FOUND", len(data))
    cols = st.columns(3)
    for i, ev in enumerate(data):
        with cols[i % 3]:
            pred_val, cap_val = get_prediction(ev['venue'])
            
            mail_body = f"Event: {ev['title']}\nVenue: {ev['venue']}\nDate: {ev['date']}\nEst. Attendance: {pred_val}"
            mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=STAFFING:{ev['title']}&body={urllib.parse.quote(mail_body)}"
            
            st.html(f"""
                <div class="event-card">
                    <span class="status-badge">{ev['type']}</span>
                    <div style="font-size: 1.1rem; font-weight: bold; margin: 12px 0 4px 0; min-height: 50px;">{ev['title']}</div>
                    <div style="color: #888; font-size: 0.85rem; margin-bottom: 8px;">📍 {ev['venue']}</div>
                    <div style="color: #555; font-size: 0.8rem;">🕒 {ev['date']}</div>
                    
                    <div class="prediction-box">
                        <div style="color: #00d4ff; font-size: 0.7rem; font-weight: bold;">ATTENDANCE PREDICTION</div>
                        <div style="font-size: 1.3rem; font-weight: bold;">~ {pred_val:,}</div>
                        <div style="color: #444; font-size: 0.65rem;">Based on venue capacity</div>
                    </div>
                    
                    <a href="{mail_url}" class="jira-btn">📩 Create Jira Task</a>
                </div>
            """)
else:
    st.warning("No live data found. Try more specific name like 'Wembley Stadium events'.")

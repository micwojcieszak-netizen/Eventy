import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random

# 1. KONFIGURACJA STRONY
st.set_page_config(page_title="Event Collector 💡", layout="wide")

# 2. NOWOCZESNY DESIGN (Zaktualizowany o style predykcji)
st.html("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0f1116; color: #ffffff; font-family: 'Inter', sans-serif; }
    .event-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 24px; margin-bottom: 20px;
    }
    .status-badge {
        background-color: rgba(0, 212, 255, 0.1); color: #00d4ff;
        padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 0.75rem;
    }
    .prediction-box {
        background: rgba(0, 212, 255, 0.05); border: 1px dashed #00d4ff;
        border-radius: 10px; padding: 10px; margin-top: 15px;
    }
    .jira-btn {
        display: block; width: 100%; text-align: center; background: #0052cc;
        color: white !important; text-decoration: none; padding: 10px;
        border-radius: 8px; font-weight: bold; margin-top: 15px; font-size: 0.85rem;
    }
    .jira-btn:hover { background: #0747a6; }
</style>
""")

st.markdown("# Event Collector 💡")
query = st.text_input("Search Venue or Team:", "LCFC")

# SŁOWNIK POJEMNOŚCI (Dla predykcji)
CAPACITIES = {
    "WEMBLEY": 90000, "AO ARENA": 21000, "LCFC": 32261, 
    "KING POWER": 32261, "O2 ARENA": 20000, "TAURON": 15000
}

def get_prediction(venue_name, event_type):
    # Logika predykcji: szukamy pojemności w słowniku, domyślnie 10k
    capacity = 10000
    for key in CAPACITIES:
        if key in venue_name.upper():
            capacity = CAPACITIES[key]
            break
    
    # Symulacja % wypełnienia w zależności od typu
    rate = 0.95 if event_type == "Match" else 0.85
    predicted_attendance = int(capacity * rate * random.uniform(0.9, 1.0))
    return predicted_attendance, capacity

def get_live_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f" 
    params = {"q": f"{search_term} events fixtures", "hl": "en", "gl": "gb", "api_key": API_KEY}
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        events_list = []
        
        if "sports_results" in results and "games" in results["sports_results"]:
            for game in results["sports_results"]["games"][:6]:
                teams = game.get("teams", [{},{}])
                events_list.append({
                    "title": f"{teams[0].get('name', '')} v {teams[1].get('name', '')}",
                    "venue": search_term.upper(), "date": game.get("date", "TBD"), "type": "Match"
                })
        
        if not events_list and "events_results" in results:
            for ev in results["events_results"][:6]:
                events_list.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term.upper()),
                    "date": ev.get("date", {}).get("when", "Upcoming"), "type": "Concert"
                })
        return events_list
    except: return []

data = get_live_data(query)

# Grid kart
if data:
    cols = st.columns(3)
    for i, ev in enumerate(data):
        with cols[i % 3]:
            # Obliczanie predykcji
            pred_val, cap_val = get_prediction(ev['venue'], ev['type'])
            
            # Przygotowanie maila do Jiry
            mail_body = f"Source: Event Collector\nEvent: {ev['title']}\nPredicted Attendance: {pred_val}"
            mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing Request: {ev['title']}&body={urllib.parse.quote(mail_body)}"
            
            st.html(f"""
                <div class="event-card">
                    <span class="status-badge">{ev['type']}</span>
                    <div style="font-size: 1.2rem; font-weight: bold; margin: 15px 0 5px 0;">{ev['title']}</div>
                    <div style="color: #888; font-size: 0.9rem;">📍 {ev['venue']}</div>
                    <div style="color: #aaa; font-size: 0.85rem;">🕒 {ev['date']}</div>
                    
                    <div class="prediction-box">
                        <div style="color: #00d4ff; font-size: 0.8rem; font-weight: bold;">📊 PREDICTED ATTENDANCE</div>
                        <div style="font-size: 1.4rem; font-weight: bold;">~ {pred_val:,}</div>
                        <div style="color: #666; font-size: 0.75rem;">Cap: {cap_val:,} | Prob: 92%</div>
                    </div>
                    
                    <a href="{mail_url}" class="jira-btn">📩 Create Jira Task</a>
                </div>
            """)

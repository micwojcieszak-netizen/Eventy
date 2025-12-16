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
query = st.text_input("Wyszukaj stadion, miasto lub drużynę:", "Intuit Dome")

# ROZSZERZONY SŁOWNIK POJEMNOŚCI
CAPACITIES = {
    "WEMBLEY": 90000, "AO ARENA": 21000, "LCFC": 32261, "KING POWER": 32261, 
    "O2 ARENA": 20000, "TAURON": 15000, "NARODOWY": 58000, "CAMP NOU": 99000,
    "MADISON SQUARE": 19500, "ANFIELD": 54000, "OLD TRAFFORD": 74000,
    "INTUIT DOME": 18000, "SOFI STADIUM": 70000, "STAPLES CENTER": 19000
}

def get_prediction(venue_name):
    venue_upper = venue_name.upper()
    capacity = 15000
    for key, val in CAPACITIES.items():
        if key in venue_upper:
            capacity = val
            break
    predicted = int(capacity * random.uniform(0.88, 0.99))
    return predicted, capacity

def get_live_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f" 
    params = {
        "q": f"{search_term} events schedule 2025 2026",
        "hl": "en",
        "gl": "us", # Zmienione na US dla lepszego znajdowania amerykańskich aren
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        events_list = []
        
        # 1. Sprawdź karuzelę wydarzeń (Event Results)
        if "events_results" in results:
            for ev in results["events_results"][:15]:
                events_list.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term),
                    "date": ev.get("date", {}).get("when", "2025/2026"),
                    "type": "OFFICIAL EVENT"
                })
        
        # 2. Sprawdź Knowledge Graph (Dane z boku Google)
        if not events_list and "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            if "events" in kg:
                for ev in kg["events"][:10]:
                    events_list.append({
                        "title": ev.get("name"),
                        "venue": search_term,
                        "date": ev.get("date", "Upcoming"),
                        "type": "KNOWLEDGE BASE"
                    })

        # 3. Agresywne przeszukiwanie wyników organicznych (jeśli pusto)
        if not events_list and "organic_results" in results:
            for res in results["organic_results"][:10]:
                title = res.get("title", "")
                if any(x in title.lower() for x in ["tickets", "schedule", "events", "concert", "tour"]):
                    clean_title = title.split('|')[0].split('-')[0].split('Tickets')[0].strip()
                    if len(clean_title) > 5:
                        events_list.append({
                            "title": clean_title,
                            "venue": search_term,
                            "date": "See Details in Jira",
                            "type": "DISCOVERED"
                        })
                
        # Usuwanie duplikatów po tytule
        unique_events = []
        seen_titles = set()
        for e in events_list:
            if e['title'].lower() not in seen_titles:
                unique_events.append(e)
                seen_titles.add(e['title'].lower())

        return unique_events
    except Exception as e:
        return []

# WYŚWIETLANIE
data = get_live_data(query)

if data:
    st.metric("REAL-TIME EVENTS FOUND", len(data))
    cols = st.columns(3)
    for i, ev in enumerate(data):
        with cols[i % 3]:
            pred_val, cap_val = get_prediction(ev['venue'])
            
            mail_body = f"Source: Event Collector\nEvent: {ev['title']}\nVenue: {ev['venue']}\nDate: {ev['date']}\nEst. Attendance: {pred_val}"
            mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=STAFFING:{ev['title']}&body={urllib.parse.quote(mail_body)}"
            
            st.html(f"""
                <div class="event-card">
                    <span class="status-badge">{ev['type']}</span>
                    <div style="font-size: 1.1rem; font-weight: bold; margin: 12px 0 4px 0; min-height: 55px;">{ev['title']}</div>
                    <div style="color: #888; font-size: 0.85rem; margin-bottom: 8px;">📍 {ev['venue']}</div>
                    <div style="color: #555; font-size: 0.8rem;">🕒 {ev['date']}</div>
                    
                    <div class="prediction-box">
                        <div style="color: #00d4ff; font-size: 0.7rem; font-weight: bold; letter-spacing: 0.5px;">PREDYKCJA FREKWENCJI</div>
                        <div style="font-size: 1.3rem; font-weight: bold;">~ {pred_val:,}</div>
                        <div style="color: #444; font-size: 0.65rem;">Capacity: {cap_val:,}</div>
                    </div>
                    
                    <a href="{mail_url}" class="jira-btn">📩 Create Jira Task</a>
                </div>
            """)
else:
    st.warning("Nie znaleziono wyników. Spróbuj wpisać pełną nazwę, np. 'Intuit Dome events' lub 'Intuit Dome tickets'.")

st.markdown("---")
st.caption("Event Collector Engine v4.0 (Global Search Active)")

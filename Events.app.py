import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random

# 1. KONFIGURACJA STRONY
st.set_page_config(page_title="Event Collector 💡", layout="wide")

# 2. DESIGN DARK MODE PREMIUM
st.html("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0b0d11; color: #ffffff; font-family: 'Inter', sans-serif; }
    .stTextInput input { background-color: #1b1e26 !important; color: white !important; border: 1px solid #333 !important; border-radius: 10px !important; }
    .event-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 22px; margin-bottom: 20px; transition: 0.3s;
    }
    .event-card:hover { border-color: #00d4ff; background: rgba(255, 255, 255, 0.05); }
    .status-badge {
        background-color: rgba(0, 212, 255, 0.1); color: #00d4ff;
        padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.7rem; text-transform: uppercase; float: right;
    }
    .prediction-box {
        background: rgba(0, 212, 255, 0.07); border-radius: 12px; padding: 12px; margin-top: 15px; border: 1px dashed rgba(0, 212, 255, 0.3);
    }
    .jira-btn {
        display: block; width: 100%; text-align: center; background: #0052cc;
        color: white !important; text-decoration: none; padding: 10px;
        border-radius: 8px; font-weight: bold; margin-top: 15px; font-size: 0.8rem;
    }
</style>
""")

st.markdown("# Event Collector 💡")

# PEŁNA BAZA POJEMNOŚCI (Twoja lista)
CAPACITIES = {
    "ACRISURE ARENA": 11000, "AO ARENA": 21000, "ATLANTA HAWKS": 16600, "STATE FARM ARENA": 16600,
    "BUFFALO SABRES": 19070, "KEYBANK CENTER": 19070, "CFG BANK ARENA": 14000, "COOP ARENA": 6300,
    "DETROIT LIONS": 65000, "FORD FIELD": 65000, "FLORIDA PANTHERS": 19250, "AMERANT BANK ARENA": 19250,
    "GOLDEN STATE WARRIORS": 18064, "CHASE CENTER": 18064, "INTUIT DOME": 18000, "KANSAS CITY CHIEFS": 76416,
    "ARROWHEAD STADIUM": 76416, "LAS VEGAS RAIDERS": 65000, "ALLEGIANT STADIUM": 65000, "LEICESTER FC": 32261,
    "KING POWER": 32261, "LA CLIPPERS": 18000, "MIAMI DOLPHINS": 65326, "HARD ROCK STADIUM": 65326,
    "MERCEDES BENZ": 71000, "NEW JERSEY DEVILS": 16514, "PRUDENTIAL CENTER": 16514, "PAYPAY DOM": 40000,
    "PHILADELPHIA EAGLES": 69176, "LINCOLN FINANCIAL": 69176, "PHOENIX SUNS": 17071, "FOOTPRINT CENTER": 17071,
    "SOFI": 70000, "TENNESSEE TITANS": 69143, "NISSAN STADIUM": 69143, "AVFC": 42682, "VILLA PARK": 42682,
    "BRIGHTON": 31800, "AMEX STADIUM": 31800, "SODEXO": 25000, "LEVY": 20000
}

def get_prediction(venue_name):
    venue_upper = venue_name.upper()
    capacity = 18000
    for key, val in CAPACITIES.items():
        if key in venue_upper:
            capacity = val
            break
    predicted = int(capacity * random.uniform(0.91, 0.99))
    return predicted, capacity

# WYSZUKIWARKA
query = st.text_input("Wyszukaj stadion, drużynę lub arenę:", "Intuit Dome")

def get_live_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f" 
    
    # Inteligentne wykrywanie regionu (USA vs Reszta Świata)
    us_keywords = ["DOME", "STADIUM", "ARENA", "CHIEFS", "RAIDERS", "EAGLES", "SUNS", "DOLPHINS", "PANTHERS"]
    region = "us" if any(x in search_term.upper() for x in us_keywords) else "gb"
    
    # Próbujemy dwóch różnych zapytań dla większej skuteczności
    search_queries = [f"{search_term} events schedule", f"{search_term} tickets 2025 2026"]
    all_events = []

    for q in search_queries:
        params = {"q": q, "hl": "en", "gl": region, "api_key": API_KEY}
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # 1. Widget Wydarzeń
            if "events_results" in results:
                for ev in results["events_results"][:10]:
                    all_events.append({
                        "title": ev.get("title"),
                        "venue": ev.get("venue", {}).get("name", search_term),
                        "date": ev.get("date", {}).get("when", "2025/2026"),
                        "type": "OFFICIAL"
                    })
            
            # 2. Wyniki Sportowe
            if "sports_results" in results and "games" in results["sports_results"]:
                for game in results["sports_results"]["games"][:5]:
                    teams = game.get("teams", [{},{}])
                    all_events.append({
                        "title": f"{teams[0].get('name', 'TBD')} vs {teams[1].get('name', 'TBD')}",
                        "venue": search_term.upper(),
                        "date": game.get("date", "Upcoming Match"),
                        "type": "MATCH"
                    })
            
            # 3. Wyniki organiczne (jeśli wciąż mało)
            if len(all_events) < 3 and "organic_results" in results:
                for res in results["organic_results"][:5]:
                    title = res.get("title", "")
                    if any(x in title.lower() for x in ["tickets", "events", "concert"]):
                        clean_title = title.split('|')[0].split('-')[0].strip()
                        all_events.append({
                            "title": clean_title,
                            "venue": search_term,
                            "date": "Check Details",
                            "type": "DISCOVERED"
                        })
        except:
            continue

    # Usuwanie duplikatów
    seen = set()
    unique_list = []
    for e in all_events:
        if e['title'].lower() not in seen:
            unique_list.append(e)
            seen.add(e['title'].lower())
            
    return unique_list

# GENEROWANIE WIDOKU
data = get_live_data(query)

if data:
    st.markdown(f"### 🗓️ Upcoming Events for {query.upper()}")
    cols = st.columns(3)
    for i, ev in enumerate(data):
        with cols[i % 3]:
            pred_val, cap_val = get_prediction(ev['venue'])
            mail_body = f"Source: Event Collector\nEvent: {ev['title']}\nVenue: {ev['venue']}\nPred. Attendance: {pred_val}"
            mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}&body={urllib.parse.quote(mail_body)}"
            
            st.html(f"""
                <div class="event-card">
                    <span class="status-badge">{ev['type']}</span>
                    <div style="font-size: 1.1rem; font-weight: bold; margin: 12px 0 4px 0; min-height: 55px; color:white;">{ev['title']}</div>
                    <div style="color: #888; font-size: 0.85rem; margin-bottom: 8px;">📍 {ev['venue']}</div>
                    <div style="color: #555; font-size: 0.8rem;">🕒 {ev['date']}</div>
                    <div class="prediction-box">
                        <div style="color: #00d4ff; font-size: 0.7rem; font-weight: bold; letter-spacing: 0.5px;">PREDYKCJA FREKWENCJI</div>
                        <div style="font-size: 1.4rem; font-weight: bold; color: #fff;">~ {pred_val:,}</div>
                        <div style="color: #444; font-size: 0.65rem;">Capacity: {cap_val:,}</div>
                    </div>
                    <a href="{mail_url}" class="jira-btn">📩 Create Jira Task</a>
                </div>
            """)
else:
    st.warning("⚠️ Brak wyników. Upewnij się, że nazwa jest poprawna lub spróbuj dopisać 'events' (np. 'AO Arena events').")

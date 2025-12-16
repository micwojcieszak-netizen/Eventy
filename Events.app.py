import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random
import re

# 1. KONFIGURACJA
st.set_page_config(page_title="Event Collector 💡", layout="wide")

# 2. DESIGN DARK MODE PREMIUM
st.html("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0b0d11; color: #ffffff; font-family: 'Inter', sans-serif; }
    .event-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 22px; margin-bottom: 20px; transition: 0.3s ease;
    }
    .event-card:hover { border-color: #00d4ff; background: rgba(255, 255, 255, 0.05); transform: translateY(-3px); }
    .status-badge {
        background-color: rgba(0, 212, 255, 0.1); color: #00d4ff;
        padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.7rem; text-transform: uppercase; float: right;
    }
    .date-text { color: #00d4ff; font-weight: bold; font-size: 0.95rem; margin-top: 10px; }
    .prediction-box {
        background: rgba(0, 212, 255, 0.07); border-radius: 12px; padding: 12px; margin-top: 15px; border: 1px dashed rgba(0, 212, 255, 0.3);
    }
    .jira-btn {
        display: block; width: 100%; text-align: center; background: #0052cc;
        color: white !important; text-decoration: none; padding: 10px;
        border-radius: 8px; font-weight: bold; margin-top: 15px; font-size: 0.85rem;
    }
</style>
""")

st.markdown("# Event Collector 💡")

# BAZA POJEMNOŚCI (Wszystkie Twoje lokalizacje)
CAPACITIES = {
    "ACRISURE": 11000, "AO ARENA": 21000, "ATLANTA HAWKS": 16600, "BUFFALO SABRES": 19070,
    "CFG BANK": 14000, "COOP ARENA": 6300, "DETROIT LIONS": 65000, "FLORIDA PANTHERS": 19250,
    "GOLDEN STATE": 18064, "INTUIT DOME": 18000, "CHIEFS": 76416, "RAIDERS": 65000,
    "LEICESTER": 32261, "CLIPPERS": 18000, "DOLPHINS": 65326, "MERCEDES BENZ": 71000,
    "DEVILS": 16514, "PAYPAY": 40000, "EAGLES": 69176, "PHOENIX SUNS": 17071,
    "SOFI": 70000, "TITANS": 69143, "VILLA PARK": 42682, "BRIGHTON": 31800
}

def get_prediction(venue_name):
    venue_upper = venue_name.upper()
    capacity = 18000
    for key, val in CAPACITIES.items():
        if key in venue_upper:
            capacity = val
            break
    predicted = int(capacity * random.uniform(0.93, 0.99))
    return predicted, capacity

query = st.text_input("Wyszukaj lokalizację (np. Intuit Dome, Leicester City, Mercedes Benz Stadium):", "Intuit Dome")

def fetch_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f"
    
    # Automatyczne dopasowanie regionu
    us_tags = ["DOME", "STADIUM", "ARENA", "CHIEFS", "RAIDERS", "EAGLES", "SUNS", "DOLPHINS", "INTUIT", "HAWKS", "LIONS"]
    region = "us" if any(x in search_term.upper() for x in us_tags) else "gb"
    
    params = {
        "q": f"{search_term} full events schedule tickets 2025 2026",
        "hl": "en",
        "gl": region,
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        res = search.get_dict()
        events = []
        
        # 1. POBIERANIE Z WIDGETU SPORTOWEGO (Najdokładniejsze godziny)
        if "sports_results" in res and "games" in res["sports_results"]:
            for g in res["sports_results"]["games"][:10]:
                t = g.get("teams", [{},{}])
                name = f"{t[0].get('name', 'TBD')} vs {t[1].get('name', 'TBD')}"
                full_date = f"{g.get('date', '')} • {g.get('time', 'TBA')}"
                events.append({"title": name, "venue": search_term.upper(), "date": full_date, "type": "Match Day"})

        # 2. POBIERANIE Z KALENDARZA WYDARZEŃ
        if "events_results" in res:
            for ev in res["events_results"][:12]:
                events.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term.upper()),
                    "date": ev.get("date", {}).get("when", "Upcoming"),
                    "type": "Live Event"
                })

        # 3. INTELIGENTNY PARSER Z WYNIKÓW ORGANICZNYCH (Jeśli brak widgetów)
        if not events and "organic_results" in res:
            for r in res["organic_results"][:8]:
                snippet = r.get("snippet", "")
                # Szukamy wzorca godziny/daty w opisie strony za pomocą Regex
                time_match = re.search(r'(\d{1,2}:\d{2}\s?(AM|PM|am|pm))', snippet)
                date_match = re.search(r'([A-Z][a-z]{2,8}\s\d{1,2})', snippet)
                
                if time_match or date_match:
                    clean_title = r.get("title").split('|')[0].split('-')[0].strip()
                    found_date = f"{date_match.group(0) if date_match else ''} {time_match.group(0) if time_match else ''}"
                    events.append({
                        "title": clean_title,
                        "venue": search_term.upper(),
                        "date": found_date if found_date.strip() else "Check in Jira",
                        "type": "Detected"
                    })

        return events
    except: return []

# GENEROWANIE
data = fetch_data(query)

if data:
    st.markdown(f"### 🏟️ Wyświetlam wyniki dla: {query.upper()}")
    cols = st.columns(3)
    for i, ev in enumerate(data):
        with cols[i % 3]:
            pred, cap = get_prediction(ev['venue'])
            mail_body = f"Event: {ev['title']}\nVenue: {ev['venue']}\nDate: {ev['date']}\nPred. Attendance: {pred}"
            mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}&body={urllib.parse.quote(mail_body)}"
            
            st.html(f"""
                <div class="event-card">
                    <span class="status-badge">{ev['type']}</span>
                    <div style="font-size: 1.15rem; font-weight: bold; margin-bottom: 5px; color:white; min-height: 55px;">{ev['title']}</div>
                    <div style="color: #888; font-size: 0.9rem;">📍 {ev['venue']}</div>
                    <div class="date-text">📅 {ev['date']}</div>
                    <div class="prediction-box">
                        <div style="color: #00d4ff; font-size: 0.7rem; font-weight: bold;">EST. ATTENDANCE</div>
                        <div style="font-size: 1.45rem; font-weight: bold; color: white;">~ {pred:,}</div>
                        <div style="color: #444; font-size: 0.65rem;">Arena Capacity: {cap:,}</div>
                    </div>
                    <a href="{mail_url}" class="jira-btn">📩 Send to Jira Support</a>
                </div>
            """)
else:
    st.warning("Nie znaleziono precyzyjnych danych. Spróbuj dodać słowo 'schedule' (np. 'AO Arena schedule').")

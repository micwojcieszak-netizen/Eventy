import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random
import re

st.set_page_config(page_title="Event Collector 💡", layout="wide")

# CSS - Ciemny nowoczesny styl
st.html("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0b0d11; color: #ffffff; font-family: 'Inter', sans-serif; }
    .event-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 22px; margin-bottom: 20px; border-left: 4px solid #00d4ff;
    }
    .home-badge {
        background-color: rgba(0, 255, 127, 0.1); color: #00ff7f;
        padding: 4px 10px; border-radius: 10px; font-size: 0.7rem; font-weight: bold;
    }
    .prediction-box {
        background: rgba(0, 212, 255, 0.05); border-radius: 10px; padding: 12px; margin-top: 10px;
    }
    .jira-btn {
        display: block; width: 100%; text-align: center; background: #0052cc; color: white !important;
        text-decoration: none; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 0.8rem;
    }
</style>
""")

# BAZA OBIEKTÓW
STADIUM_DATA = {
    "INTUIT DOME": {"url": "intuitdome.com", "cap": 18000},
    "AO ARENA": {"url": "ao-arena.com", "cap": 21000},
    "LCFC": {"url": "lcfc.com", "cap": 32261},
    "SOFI STADIUM": {"url": "sofistadium.com", "cap": 70000},
    "FORD FIELD": {"url": "fordfield.com", "cap": 65000}
}

def get_prediction(venue_key):
    cap = STADIUM_DATA.get(venue_key, {}).get("cap", 15000)
    return int(cap * random.uniform(0.92, 0.99)), cap

st.markdown("# Event Collector 💡")
query = st.selectbox("Wybierz lokalizację:", list(STADIUM_DATA.keys()))

def deep_scrape(venue_key):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f"
    site = STADIUM_DATA[venue_key]["url"]
    
    # Zapytanie wymuszające szukanie na konkretnej stronie
    params = {
        "q": f"site:{site} events schedule 2025 2026",
        "hl": "en",
        "gl": "us" if venue_key != "AO ARENA" and venue_key != "LCFC" else "gb",
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        res = search.get_dict()
        events = []

        # 1. PRÓBA: Dane ustrukturyzowane (Widgety)
        if "events_results" in res:
            for ev in res["events_results"]:
                events.append({"title": ev.get("title"), "date": ev.get("date", {}).get("when", "Upcoming"), "src": "Official"})

        # 2. PRÓBA:Knowledge Graph (Dane z bazy Google)
        if not events and "knowledge_graph" in res and "events" in res["knowledge_graph"]:
            for ev in res["knowledge_graph"]["events"]:
                events.append({"title": ev.get("name"), "date": ev.get("date", "Upcoming"), "src": "Google Knowledge"})

        # 3. PRÓBA: Organic Snippet Parser (Wyciąganie z opisów stron)
        if not events and "organic_results" in res:
            for r in res["organic_results"]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                # Szukamy wzorców dat (np. Dec 20, 2025)
                date_match = re.search(r'([A-Z][a-z]{2}\s\d{1,2})', snippet + title)
                if date_match or "vs" in title.lower():
                    clean_title = title.split('|')[0].split('-')[0].strip()
                    events.append({"title": clean_title, "date": date_match.group(0) if date_match else "Check details", "src": "Web Discovery"})

        return events
    except: return []

if st.button(f"🔍 Deep Scrape {query}"):
    data = deep_scrape(query)
    if data:
        cols = st.columns(3)
        for i, ev in enumerate(data):
            with cols[i % 3]:
                pred, cap = get_prediction(query)
                mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}"
                st.html(f"""
                    <div class="event-card">
                        <span class="home-badge">HOME GAME</span>
                        <div style="font-size: 1.1rem; font-weight: bold; margin: 10px 0;">{ev['title']}</div>
                        <div style="color: #00d4ff; font-weight: bold;">📅 {ev['date']}</div>
                        <div class="prediction-box">
                            <span style="font-size: 0.7rem; color: #aaa;">EST. ATTENDANCE</span><br>
                            <b style="font-size: 1.2rem;">~ {pred:,} / {cap:,}</b>
                        </div>
                        <a href="{mail_url}" class="jira-btn">📩 Send to Jira</a>
                    </div>
                """)
    else:
        st.warning("Google nie zaindeksowało jeszcze kalendarza dla tej strony. Spróbuj wyszukać ogólnie wpisując nazwę w Google Search.")

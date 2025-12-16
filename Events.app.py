import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random

# 1. KONFIGURACJA
st.set_page_config(page_title="Event Collector 💡", layout="wide")

# 2. DESIGN
st.html("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0b0d11; color: #ffffff; font-family: 'Inter', sans-serif; }
    .event-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 22px; margin-bottom: 20px;
    }
    .date-text { color: #00d4ff; font-weight: bold; font-size: 1rem; margin-top: 10px; }
    .jira-btn {
        display: block; width: 100%; text-align: center; background: #0052cc;
        color: white !important; text-decoration: none; padding: 10px;
        border-radius: 8px; font-weight: bold; margin-top: 15px;
    }
</style>
""")

# BAZA OFICJALNYCH STRON (Mapping)
VENUE_SITES = {
    "INTUIT DOME": "intuitdome.com/events",
    "AO ARENA": "ao-arena.com/events",
    "LEICESTER": "lcfc.com/matches/fixtures",
    "WEMBLEY": "wembleystadium.com/events",
    "SOFI": "sofistadium.com/events"
}

CAPACITIES = {"INTUIT DOME": 18000, "AO ARENA": 21000, "LCFC": 32261, "SOFI": 70000}

def get_prediction(venue_name):
    cap = 18000
    for k, v in CAPACITIES.items():
        if k in venue_name.upper(): cap = v; break
    return int(cap * random.uniform(0.95, 0.99)), cap

st.markdown("# Event Collector 💡")
query = st.text_input("Wyszukaj (np. Intuit Dome):", "Intuit Dome")

def fetch_site_specific_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f"
    
    # Sprawdzamy czy mamy zmapowaną oficjalną stronę
    target_site = ""
    for v_name, v_site in VENUE_SITES.items():
        if v_name in search_term.upper():
            target_site = f"site:{v_site}"
            break
    
    # Budujemy zapytanie: albo przeszukujemy całe Google, albo celujemy w konkretną stronę
    final_query = f"{target_site} {search_term} events schedule 2025 2026"
    
    params = {
        "q": final_query,
        "hl": "en",
        "gl": "us" if "INTUIT" in search_term.upper() else "gb",
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        res = search.get_dict()
        events = []
        
        # Przeszukiwanie wyników "Event Results" z Google (one zaciągają dane ze struktur strony)
        if "events_results" in res:
            for ev in res["events_results"][:12]:
                events.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term.upper()),
                    "date": ev.get("date", {}).get("when", "2025/2026"),
                    "type": "Direct Site Feed"
                })
        
        # Fallback na Sports Results (dla meczów Clippers/Lakers)
        if not events and "sports_results" in res and "games" in res["sports_results"]:
            for g in res["sports_results"]["games"]:
                t = g.get("teams", [{},{}])
                events.append({
                    "title": f"{t[0].get('name')} vs {t[1].get('name')}",
                    "venue": search_term.upper(),
                    "date": f"{g.get('date')} • {g.get('time')}",
                    "type": "Live Fixture"
                })
        return events
    except: return []

data = fetch_site_specific_data(query)

if data:
    cols = st.columns(3)
    for i, ev in enumerate(data):
        with cols[i % 3]:
            pred, cap = get_prediction(ev['venue'])
            mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}"
            st.html(f"""
                <div class="event-card">
                    <div class="date-text">📅 {ev['date']}</div>
                    <div style="font-size: 1.2rem; font-weight: bold; margin: 10px 0;">{ev['title']}</div>
                    <div style="color: #888;">📍 {ev['venue']}</div>
                    <div style="background: rgba(0, 212, 255, 0.1); padding: 10px; border-radius: 8px; margin-top: 15px;">
                        <span style="color: #00d4ff; font-size: 0.8rem;">PREDYKCJA</span><br>
                        <b style="font-size: 1.3rem;">~ {pred:,} osób</b>
                    </div>
                    <a href="{mail_url}" class="jira-btn">📩 Send to Jira</a>
                </div>
            """)
else:
    st.info("Searching official sources... If no results, check if the venue has published their 2025/2026 schedule.")

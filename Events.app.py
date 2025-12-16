import streamlit as st
from serpapi import GoogleSearch
import urllib.parse
import random

# 1. KONFIGURACJA I DESIGN
st.set_page_config(page_title="Event Collector 💡", layout="wide")

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

# 2. BAZA MAPOWANIA STRON I POJEMNOŚCI
# Skrypt używa tego, by wiedzieć gdzie scrapować i jaka jest pojemność
STADIUM_DATA = {
    "INTUIT DOME": {"url": "intuitdome.com/events", "cap": 18000},
    "AO ARENA": {"url": "ao-arena.com/events", "cap": 21000},
    "LCFC": {"url": "lcfc.com/matches/fixtures", "cap": 32261},
    "SOFI STADIUM": {"url": "sofistadium.com/events", "cap": 70000},
    "MERCEDES BENZ": {"url": "mercedesbenzstadium.com/events", "cap": 71000},
    "FORD FIELD": {"url": "fordfield.com/events", "cap": 65000},
    "PRUDENTIAL CENTER": {"url": "prucenter.com/events", "cap": 16514}
}

def get_prediction(venue_key):
    cap = STADIUM_DATA.get(venue_key, {}).get("cap", 15000)
    return int(cap * random.uniform(0.94, 0.98)), cap

st.markdown("# Event Collector 💡")
query = st.selectbox("Wybierz lokalizację do scrapowania:", list(STADIUM_DATA.keys()))

def deep_scrape_events(venue_key):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f"
    target = STADIUM_DATA[venue_key]["url"]
    
    # Budujemy zapytanie celowane w konkretną domenę
    # To zmusza Google do bycia "pośrednikiem" w scrapowaniu strony
    params = {
        "q": f"site:{target} events schedule 2025 2026",
        "hl": "en",
        "gl": "us" if venue_key not in ["AO ARENA", "LCFC"] else "gb",
        "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        res = search.get_dict()
        events = []
        
        # Ekstrakcja z widgetu Event Results (Google parsuje kod strony za nas)
        if "events_results" in res:
            for ev in res["events_results"][:12]:
                title = ev.get("title", "")
                venue_from_site = ev.get("venue", {}).get("name", "").upper()
                
                # WERYFIKACJA: Czy to faktycznie Home Game/Event?
                is_home = False
                if venue_key in venue_from_site or venue_key in title.upper():
                    is_home = True
                elif "vs" in title.lower() and venue_key in title.upper().split("VS")[0]:
                    is_home = True # Drużyna gospodarzy jest zazwyczaj wymieniona jako pierwsza

                events.append({
                    "title": title,
                    "date": ev.get("date", {}).get("when", "Upcoming"),
                    "is_home": is_home,
                    "raw_venue": venue_from_site
                })
        return events
    except: return []

# 3. WYŚWIETLANIE WYNIKÓW
if st.button(f"Scrapuj dane z {STADIUM_DATA[query]['url']}"):
    with st.spinner("Deep scraping in progress..."):
        data = deep_scrape_events(query)
        
        if data:
            cols = st.columns(3)
            for i, ev in enumerate(data):
                with cols[i % 3]:
                    pred, cap = get_prediction(query)
                    
                    # Logika Jiry
                    mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}"
                    
                    st.html(f"""
                        <div class="event-card">
                            <div style="display: flex; justify-content: space-between;">
                                <span class="home-badge">{'🏠 HOME EVENT' if ev['is_home'] else '📍 AWAY/OTHER'}</span>
                            </div>
                            <div style="font-size: 1.1rem; font-weight: bold; margin: 10px 0; color: white;">{ev['title']}</div>
                            <div style="color: #00d4ff; font-weight: bold;">📅 {ev['date']}</div>
                            <div style="color: #888; font-size: 0.8rem; margin-top: 5px;">Source: {STADIUM_DATA[query]['url']}</div>
                            
                            <div class="prediction-box">
                                <span style="font-size: 0.7rem; color: #aaa;">EST. ATTENDANCE</span><br>
                                <b style="font-size: 1.2rem;">~ {pred:,} / {cap:,}</b>
                            </div>
                            <a href="{mail_url}" class="jira-btn">📩 Create Ticket</a>
                        </div>
                    """)
        else:
            st.warning("Nie znaleziono ustrukturyzowanych danych na tej stronie. Spróbuj innego obiektu.")

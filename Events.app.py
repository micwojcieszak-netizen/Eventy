import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="StadiumStaffer Dashboard", layout="wide")

# STYLIZACJA CSS (To sprawia, że wygląda jak oryginał)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    .event-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #ffca28; /* Żółty pasek dla Upcoming */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .event-title { font-weight: bold; font-size: 1.2rem; color: #1a1a1a; }
    .event-venue { color: #666; font-size: 0.9rem; margin-top: 5px; }
    .event-time { color: #444; font-size: 0.9rem; margin-top: 10px; display: flex; align-items: center; }
    .status-badge {
        background-color: #fff4e6;
        color: #d9480f;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .countdown { color: #d9480f; font-weight: bold; margin-top: 10px; font-size: 0.9rem; }
    </style>
    """, unsafe_content_html=True)

# NAGŁÓWEK
st.title("Schedule Overview")
st.write("Upcoming events across all venues in the next 14 days.")

# STATYSTYKI
col_stat1, col_stat2 = st.columns(2)
col_stat1.metric("UPCOMING (2 WEEKS)", "2", "Events approaching")
col_stat2.metric("TRACKED VENUES", "1", "Updates checked daily")

st.markdown("### 🗓️ Upcoming Schedule")

# FUNKCJA POBIERAJĄCA DANE (Automatyczna)
def get_lcfc_data():
    # W prawdziwym świecie tutaj robimy requests.get("url_do_terminarza")
    # Poniżej symulujemy dane, które scraper wyciągnąłby ze strony
    data = [
        {"match": "Leicester City v Watford", "date": "2025-12-26 15:00", "status": "Upcoming"},
        {"match": "Leicester City v Derby County", "date": "2025-12-29 19:45", "status": "Upcoming"},
        {"match": "Leicester City v West Bromwich Albion", "date": "2026-01-05 20:00", "status": "Scheduled"},
        {"match": "Leicester City v Coventry City", "date": "2026-01-17 13:30", "status": "Scheduled"},
    ]
    return data

# WYŚWIETLANIE KART
events = get_lcfc_data()
cols = st.columns(2)

for i, ev in enumerate(events):
    with cols[i % 2]:
        dt = datetime.strptime(ev['date'], '%Y-%m-%d %H:%M')
        days_diff = (dt - datetime.now()).days
        
        # Generowanie karty HTML
        st.markdown(f"""
            <div class="event-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="event-title">{ev['match']}</div>
                    <div class="status-badge">⚠️ {ev['status']}</div>
                </div>
                <div class="event-venue">LCFC</div>
                <div class="event-time">🕒 {dt.strftime('%A, %b %d, %Y • %H:%M')}</div>
                <div class="countdown">Happening in {max(0, days_diff)} days</div>
            </div>
        """, unsafe_content_html=True)

if st.button("🔄 Refresh All"):
    st.rerun()

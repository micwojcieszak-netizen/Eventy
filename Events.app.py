import streamlit as st
import requests
from datetime import datetime

# 1. Konfiguracja strony (musi być na samym początku!)
st.set_page_config(page_title="Stadium Dashboard", layout="wide")

# 2. Stylizacja (Uproszczona, aby uniknąć błędów TypeError)
style_css = """
    <style>
    .event-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #ffca28;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: black;
    }
    .status-badge {
        background-color: #fff4e6;
        color: #d9480f;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
"""
st.markdown(style_css, unsafe_content_html=True)

# 3. Treść strony
st.title("Schedule Overview")
st.write("Upcoming events for the next 14 days.")

# Statystyki
c1, c2 = st.columns(2)
c1.metric("UPCOMING (2 WEEKS)", "2")
c2.metric("TRACKED VENUES", "1")

# Dane
events = [
    {"match": "Leicester City v Watford", "date": "2025-12-26 15:00", "status": "Upcoming"},
    {"match": "Leicester City v Derby County", "date": "2025-12-29 19:45", "status": "Upcoming"}
]

# 4. Wyświetlanie kart
cols = st.columns(2)
for i, ev in enumerate(events):
    dt = datetime.strptime(ev['date'], '%Y-%m-%d %H:%M')
    with cols[i % 2]:
        st.markdown(f"""
            <div class="event-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>{ev['match']}</b>
                    <span class="status-badge">{ev['status']}</span>
                </div>
                <div style="color: gray; font-size: 0.9rem;">LCFC</div>
                <div style="margin-top: 10px;">🕒 {dt.strftime('%A, %b %d, %Y')}</div>
            </div>
        """, unsafe_content_html=True)

import streamlit as st
from serpapi import GoogleSearch
from datetime import datetime
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(page_title="StadiumStaffer", layout="wide")

# 2. Bezpieczne ładowanie stylów (rozwiązuje błąd TypeError)
st.write('<style>div.stMarkdown { font-family: sans-serif; }</style>', unsafe_content_html=True)

# Definicja stylu jako czysty tekst
css = """
<style>
    .event-card {
        background-color: #fff9f2;
        border: 1px solid #ffe8cc;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .status-badge {
        background-color: #fff4e6;
        color: #d9480f;
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
        float: right;
    }
    .countdown {
        color: #d9480f;
        font-weight: bold;
        margin-top: 10px;
    }
</style>
"""
st.markdown(css, unsafe_content_html=True)

# 3. Nagłówek i wyszukiwarka
st.title("Schedule Overview")
query = st.text_input("Enter venue or team name:", "LCFC")

# 4. Funkcja pobierająca dane z Google (SerpApi)
def get_live_data(q):
    params = {
        "q": f"{q} fixtures events",
        "hl": "en",
        "gl": "gb",
        "api_key": "TWÓJ_KLUCZ_SERPAPI" # <--- WKLEJ KLUCZ TUTAJ
    }
    try:
        search = GoogleSearch(params)
        res = search.get_dict()
        events = []
        # Przeszukiwanie wyników sportowych lub eventowych Google
        if "sports_results" in res and "games" in res["sports_results"]:
            for game in res["sports_results"]["games"][:6]:
                events.append({
                    "title": game.get("teams", [{},{}])[0].get("name", "") + " v " + game.get("teams", [{},{}])[1].get("name", ""),
                    "date": game.get("date", "Upcoming"),
                    "venue": q.upper(),
                    "status": "Upcoming"
                })
        elif "events_results" in res:
            for ev in res["events_results"][:6]:
                events.append({
                    "title": ev.get("title"),
                    "date": ev.get("date", {}).get("when", "Upcoming"),
                    "venue": ev.get("venue", {}).get("name", q),
                    "status": "Scheduled"
                })
        return events
    except:
        return []

# 5. Budowanie widoku (Karty jak na zdjęciu)
if query:
    data = get_live_data(query)
    if data:
        st.write(f"Upcoming events across venues in the next 14 days.")
        
        # Statystyki (uproszczone)
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("UPCOMING (2 WEEKS)", len(data))
        col_s2.metric("TRACKED VENUES", "1")

        # Karty w dwóch kolumnach
        cols = st.columns(2)
        for i, ev in enumerate(data):
            with cols[i % 2]:
                card_html = f"""
                <div class="event-card">
                    <span class="status-badge">⚠️ {ev['status']}</span>
                    <div style="font-weight: bold; font-size: 1.1rem; color: black;">{ev['title']}</div>
                    <div style="color: #666; font-size: 0.9rem;">{ev['venue']}</div>
                    <div style="margin-top: 10px; color: black;">🕒 {ev['date']}</div>
                    <div class="countdown">Event synchronized live</div>
                </div>
                """
                st.markdown(card_html, unsafe_content_html=True)
    else:
        st.warning("No live data found. Check your API Key or try a different name.")

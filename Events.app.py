import streamlit as st
from serpapi import GoogleSearch

# 1. KONFIGURACJA STRONY
st.set_page_config(page_title="Event Collector 💡", layout="wide")

# 2. NOWOCZESNY CZARNY DESIGN (CSS)
st.html("""
<style>
    /* Główne tło i czcionka */
    [data-testid="stAppViewContainer"] {
        background-color: #0f1116;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Stylizacja paska bocznego i nagłówków */
    h1, h2, h3 { color: #ffffff !important; font-weight: 700 !important; }
    
    /* Stylizacja inputa */
    .stTextInput input {
        background-color: #1b1e26 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
    }

    /* KARTY EVENTÓW - GLASSMORPHISM */
    .event-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .event-card:hover {
        transform: translateY(-5px);
        border-color: #00d4ff; /* Neonowy błękit przy najechaniu */
    }

    /* TAGI I STATUSY */
    .status-badge {
        background-color: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .event-title { 
        font-size: 1.3rem; 
        margin-top: 15px; 
        margin-bottom: 5px; 
        color: #ffffff; 
    }
    
    .event-venue { color: #888; font-size: 0.95rem; margin-bottom: 15px; }
    
    .live-update {
        color: #00d4ff;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 15px;
    }

    /* Statystyki na górze */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px !important;
        border: 1px solid #333;
    }
</style>
""")

# 3. TYTUŁ I OPIS
st.markdown("# Event Collector 💡")
st.write("Find upcoming events worldwide with real-time data.")

# Wyszukiwarka
query = st.text_input("Search Venue or Team:", "Wembley Stadium")

# 4. POBIERANIE DANYCH (SerpApi)
def get_live_data(search_term):
    API_KEY = "9ce768d285f42807066e50e234bb6f0caa0c17bb3c63c62d42e2ead0a679513f" 
    params = {
        "q": f"{search_term} events fixtures schedule",
        "hl": "en", "gl": "gb", "api_key": API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        events_list = []
        
        # Logika dla meczów sportowych
        if "sports_results" in results and "games" in results["sports_results"]:
            for game in results["sports_results"]["games"][:6]:
                teams = game.get("teams", [{},{}])
                events_list.append({
                    "title": f"{teams[0].get('name', '')} v {teams[1].get('name', '')}",
                    "venue": search_term.upper(),
                    "date": game.get("date", "TBD"),
                    "type": "Match"
                })
        
        # Logika dla koncertów i wydarzeń
        if not events_list and "events_results" in results:
            for ev in results["events_results"][:6]:
                events_list.append({
                    "title": ev.get("title"),
                    "venue": ev.get("venue", {}).get("name", search_term.upper()),
                    "date": ev.get("date", {}).get("when", "Upcoming"),
                    "type": "Concert / Event"
                })
        return events_list
    except:
        return []

# 5. GENEROWANIE DASHBOARDU
data = get_live_data(query)

# Statystyki
c1, c2 = st.columns(2)
with c1:
    st.metric("UPCOMING EVENTS", len(data))
with c2:
    st.metric("ACTIVE TRACKING", query.upper())

st.markdown("### 🗓️ Upcoming Schedule")

# Wyświetlanie kart
if data:
    cols = st.columns(3) # Zmieniamy na 3 kolumny dla lepszego wyglądu na dużych ekranach
    for i, ev in enumerate(data):
        with cols[i % 3]:
            st.html(f"""
                <div class="event-card">
                    <span class="status-badge">{ev['type']}</span>
                    <div class="event-title">{ev['title']}</div>
                    <div class="event-venue">📍 {ev['venue']}</div>
                    <div style="color: #aaa;">🕒 {ev['date']}</div>
                    <div class="live-update">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        Live Data Update
                    </div>
                </div>
            """)
else:
    st.info("No events found. Check your search query.")

# Stopka
st.markdown("---")
st.caption("Event Collector v2.0 • Powered by SerpApi")

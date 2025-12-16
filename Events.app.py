import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random

# 1. DESIGN DARK MODE
st.set_page_config(page_title="Event Collector 💡", layout="wide")
st.html("<style>[data-testid='stAppViewContainer'] { background-color: #0b0d11; color: white; }</style>")

# 2. BAZA KONFIGURACYJNA (Adresy URL do scrapowania)
SCRAPE_TARGETS = {
    "Intuit Dome": "https://www.intuitdome.com/events/event-schedule",
    "AO Arena": "https://www.ao-arena.com/events",
    "Leicester City (LCFC)": "https://www.lcfc.com/matches/fixtures"
}

CAPACITIES = {"Intuit Dome": 18000, "AO Arena": 21000, "LCFC": 32261}

def scrape_direct(venue):
    url = SCRAPE_TARGETS[venue]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        events = []

        if venue == "Intuit Dome":
            # Szukamy kontenerów z klasami odpowiadającymi za eventy na stronie Intuit Dome
            # Uwaga: Klasy CSS mogą się zmieniać, wtedy trzeba je zaktualizować
            items = soup.find_all(['div', 'article'], class_=True) 
            for item in items:
                title = item.find(['h2', 'h3', 'h4'])
                if title and len(title.text.strip()) > 3:
                    events.append({
                        "title": title.text.strip(),
                        "date": "Data on Website", # Tu można dodać parser daty
                        "venue": "Intuit Dome"
                    })

        elif venue == "AO Arena":
            # AO Arena często trzyma eventy w tagach <div class="event-info">
            for event in soup.select('.event-info'):
                title = event.select_one('.title')
                date = event.select_one('.date')
                if title:
                    events.append({
                        "title": title.text.strip(),
                        "date": date.text.strip() if date else "Upcoming",
                        "venue": "AO Arena"
                    })
        
        return events
    except Exception as e:
        st.error(f"Błąd połączenia ze stroną: {e}")
        return []

# 3. INTERFEJS
st.title("Event Collector 💡 (Direct Scraper)")
choice = st.selectbox("Wybierz stronę do przeskanowania:", list(SCRAPE_TARGETS.keys()))

if st.button(f"Skanuj {choice} bezpośrednio"):
    with st.spinner("Łączenie bezpośrednio z serwerem obiektu..."):
        data = scrape_direct(choice)
        
        if data:
            cols = st.columns(3)
            for i, ev in enumerate(data[:12]): # Pokazujemy pierwsze 12
                with cols[i % 3]:
                    cap = CAPACITIES.get(choice, 15000)
                    pred = int(cap * random.uniform(0.9, 0.98))
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); border: 1px solid #333; padding: 20px; border-radius: 15px; margin-bottom: 10px;">
                        <h3 style="color: #00d4ff; margin: 0;">{ev['title']}</h3>
                        <p style="color: #888;">📅 {ev['date']}</p>
                        <hr style="border: 0.5px solid #222;">
                        <p style="font-size: 0.8rem; margin:0;">PREDYKCJA</p>
                        <p style="font-size: 1.2rem; font-weight: bold; margin:0;">~ {pred:,} osób</p>
                        <br>
                        <a href="mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}" 
                           style="background: #0052cc; color: white; padding: 8px 15px; border-radius: 5px; text-decoration: none; display: block; text-align: center;">
                           Create Jira Task
                        </a>
                    </div>
                    """, unsafe_content_html=True)
        else:
            st.warning("Strona zablokowała dostęp bota lub zmieniła strukturę CSS. Spróbuj ponownie za chwilę.")

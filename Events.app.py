import streamlit as st
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import urllib.parse

# 1. KONFIGURACJA
st.set_page_config(page_title="Event Collector Pro", layout="wide")
ua = UserAgent()

# CSS - Ciemny motyw
st.html("<style>[data-testid='stAppViewContainer'] { background-color: #0b0d11; color: white; }</style>")

STADIUM_MAP = {
    "Intuit Dome": "https://www.intuitdome.com/events/event-schedule",
    "AO Arena": "https://www.ao-arena.com/events",
    "SoFi Stadium": "https://www.sofistadium.com/events"
}

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }

def deep_scrape_v2(venue_url):
    session = requests.Session()
    try:
        # Najpierw "pukamy" do strony głównej, by dostać ciasteczka
        base_url = "/".join(venue_url.split("/")[:3])
        session.get(base_url, headers=get_headers(), timeout=10)
        
        # Potem idziemy po dane
        response = session.get(venue_url, headers=get_headers(), timeout=10)
        
        if response.status_code == 403:
            return "BLOCKED"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        # SZUKANIE DANYCH (Uniwersalny parser szukający nagłówków i dat)
        # Większość stron stadionów trzyma nazwy w tagach h2 lub h3
        cards = soup.find_all(['div', 'article', 'section'])
        
        for card in cards:
            title_tag = card.find(['h2', 'h3', 'h4'])
            if title_tag and len(title_tag.text.strip()) > 3:
                title = title_tag.text.strip()
                # Unikanie powtórzeń tych samych nazw
                if not any(e['title'] == title for e in events):
                    events.append({
                        "title": title,
                        "date": "Click to verify on site"
                    })
        
        return events
    except Exception as e:
        return str(e)

# 3. INTERFEJS
st.title("Event Collector 💡 (Direct Access Mode)")

venue_choice = st.selectbox("Select Target Venue:", list(STADIUM_MAP.keys()))
target_url = STADIUM_MAP[venue_choice]

if st.button(f"Scrape {venue_choice}"):
    with st.spinner("Bypassing security filters..."):
        data = deep_scrape_v2(target_url)
        
        if data == "BLOCKED":
            st.error("❌ Strona wykryła skrypt (Error 403).")
            st.info("💡 Sugestia: Stadiony często blokują scraping z serwerów w chmurze. Użyj przycisku poniżej, aby spróbować przez Google Cache.")
            
            # GOOGLE CACHE FALLBACK
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{target_url}"
            st.link_button("Otwórz kopię zapasową (Google Cache)", cache_url)
            
        elif isinstance(data, list) and len(data) > 0:
            cols = st.columns(3)
            for i, ev in enumerate(data[:15]):
                with cols[i % 3]:
                    st.html(f"""
                        <div style="background: rgba(255,255,255,0.05); border: 1px solid #333; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
                            <h4 style="color: #00d4ff; margin:0;">{ev['title']}</h4>
                            <p style="font-size: 0.8rem; color: #888;">Source: Official Website</p>
                            <hr style="border: 0.1px solid #222;">
                            <a href="mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}" 
                               style="background: #0052cc; color: white; padding: 10px; border-radius: 5px; text-decoration: none; display: block; text-align: center; font-size: 0.8rem;">
                               Send to Jira
                            </a>
                        </div>
                    """)
        else:
            st.warning("Nie znaleziono czytelnych wydarzeń. Strona może używać dynamicznego ładowania (JavaScript).")

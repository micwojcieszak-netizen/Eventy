import streamlit as st
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import re
import urllib.parse

# 1. KONFIGURACJA
st.set_page_config(page_title="Event Collector Pro", layout="wide")
ua = UserAgent()

# CSS - Dark Mode
st.html("<style>[data-testid='stAppViewContainer'] { background-color: #0b0d11; color: white; }</style>")

# ROZSZERZONA BAZA (Lokalizacja: Pojemność)
STADIUM_DATA = {
    "Intuit Dome": {"url": "https://www.intuitdome.com/events/event-schedule", "cap": 18000},
    "AO Arena": {"url": "https://www.ao-arena.com/events", "cap": 21000},
    "Leicester City": {"url": "https://www.lcfc.com/matches/fixtures", "cap": 32261},
    "SoFi Stadium": {"url": "https://www.sofistadium.com/events", "cap": 70000}
}

def extract_date_and_time(text):
    """Szuka daty i godziny w tekście za pomocą wyrażeń regularnych."""
    # Szuka godzin typu 7:30 PM lub 19:30
    time_match = re.search(r'(\d{1,2}:\d{2}\s?(AM|PM|am|pm)?)', text)
    # Szuka dat typu Dec 20 lub 20.12
    date_match = re.search(r'([A-Z][a-z]{2}\s\d{1,2})|(\d{1,2}/\d{1,2}/\d{2,4})', text)
    
    found_time = time_match.group(0) if time_match else ""
    found_date = date_match.group(0) if date_match else "Upcoming"
    
    return f"{found_date} {found_time}".strip()

def get_prediction(venue_name):
    cap = STADIUM_DATA.get(venue_name, {}).get("cap", 15000)
    return int(cap * random.uniform(0.92, 0.98)), cap

def deep_scrape(venue_name):
    url = STADIUM_DATA[venue_name]["url"]
    headers = {"User-Agent": ua.random}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return "BLOCKED"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        
        # Szukamy kontenerów, które mogą zawierać info o evencie
        # Większość stron używa article, section lub div z klasą 'event'
        items = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'event|card|item', re.I))
        
        if not items: # Fallback jeśli klasy są nietypowe
            items = soup.find_all(['h2', 'h3'])

        for item in items:
            text = item.get_text(separator=' ')
            title_tag = item.find(['h2', 'h3', 'h4']) or item
            title = title_tag.get_text().strip()
            
            if len(title) > 5 and not any(e['title'] == title for e in events):
                full_info = extract_date_and_time(text)
                events.append({
                    "title": title[:60],
                    "date_time": full_info if len(full_info) > 2 else "Check Official Site"
                })
        
        return events[:15] # Limit 15 wyników
    except: return []

# 3. INTERFEJS
st.title("Event Collector 💡")
choice = st.selectbox("Wybierz lokalizację:", list(STADIUM_DATA.keys()))

if st.button(f"Scrape & Predict: {choice}"):
    with st.spinner("Analizowanie strony i generowanie predykcji..."):
        results = deep_scrape(choice)
        
        if results == "BLOCKED":
            st.error("Strona zablokowała dostęp bota. Użyj Google Search API lub sprawdź ręcznie.")
        elif results:
            cols = st.columns(3)
            for i, ev in enumerate(results):
                with cols[i % 3]:
                    pred, cap = get_prediction(choice)
                    mail_url = f"mailto:support@aifi-ml.atlassian.net?subject=Staffing:{ev['title']}"
                    
                    st.html(f"""
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(0,212,255,0.2); 
                                    padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 5px solid #00d4ff;">
                            <div style="color: #00d4ff; font-weight: bold; font-size: 0.9rem;">📅 {ev['date_time']}</div>
                            <div style="font-size: 1.1rem; font-weight: bold; margin: 10px 0; color: white; min-height: 50px;">{ev['title']}</div>
                            
                            <div style="background: rgba(0, 212, 255, 0.07); padding: 10px; border-radius: 10px; margin-top: 10px;">
                                <div style="color: #aaa; font-size: 0.7rem; font-weight: bold;">ATTENDANCE PREDICTION</div>
                                <div style="font-size: 1.4rem; font-weight: bold; color: white;">~ {pred:,}</div>
                                <div style="color: #444; font-size: 0.65rem;">Capacity: {cap:,}</div>
                            </div>
                            
                            <a href="{mail_url}" style="display: block; width: 100%; text-align: center; background: #0052cc; 
                               color: white !important; text-decoration: none; padding: 10px; border-radius: 8px; 
                               margin-top: 15px; font-weight: bold; font-size: 0.8rem;">
                               📩 Send to Jira
                            </a>
                        </div>
                    """)
        else:
            st.warning("Nie znaleziono wydarzeń. Strona może wymagać JavaScript (Playwright).")

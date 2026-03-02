import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ====== GOOGLE SHEET CONNECTION ======

credentials_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(credentials_json)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 👉 METTI QUI IL TUO ID REALE
sheet = client.open_by_key("1yzlJ--HTsqvdUdiaASZbQMoC2jaE0tvZ-g2vvwVE4GY").sheet1
# ====== CARICA URL GIÀ PRESENTI ======

existing_urls = set()

try:
    records = sheet.get_all_records()
    for row in records:
        if "URL" in row and row["URL"]:
            existing_urls.add(row["URL"])
except Exception as e:
    print("Errore lettura sheet:", e)
    
# ====== SCRAPING FUNCTION ======

def check_site(url, regione, ente):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        titles = soup.find_all("a")[:10]
        results = []

        for link in titles:
            text = link.get_text(strip=True)
            href = link.get("href")

            if text and href:
                score = 0
                keywords = [
                    "promozione",
                    "marketing",
                    "turismo",
                    "wedding",
                    "eventi",
                    "comunicazione",
                    "campagna",
                ]

                for word in keywords:
                    if word.lower() in text.lower():
                        score += 2

                if score > 0 and href not in existing_urls:
                    result = {
                        "regione": regione,
                        "ente": ente,
                        "titolo": text,
                        "url": href,
                        "score": score,
                        "data": datetime.today().strftime("%Y-%m-%d")
                    }

                    results.append(result)

                    # Scrive subito nello Sheet
                    sheet.append_row([
                        regione,
                        ente,
                        "Bando/Avviso",
                        text,
                        href,
                        result["data"],
                        "",
                        "",
                        "",
                        score,
                        "",
                        "",
                        "Nuovo"
                    ])

        existing_urls.add(href)
        return results

    except Exception as e:
        print("Errore:", e)
        return []


# ====== MAIN ======

if __name__ == "__main__":

    sites = [
        {
            "regione": "Toscana",
            "ente": "Toscana Promozione Turistica",
            "url": "https://www.toscanapromozione.it/"
        },
        {
            "regione": "Puglia",
            "ente": "Pugliapromozione",
            "url": "https://www.agenziapugliapromozione.it/"
        },
        {
            "regione": "Piemonte",
            "ente": "Visit Piemonte",
            "url": "https://www.visitpiemonte.it/"
        },
        {
            "regione": "Friuli Venezia Giulia",
            "ente": "PromoTurismoFVG",
            "url": "https://www.turismofvg.it/"
        },
        {
            "regione": "Sicilia",
            "ente": "Assessorato Turismo Sicilia",
            "url": "https://www.siciliatourism.com/"
        },
        {
            "regione": "Marche",
            "ente": "Regione Marche Turismo",
            "url": "https://www.turismo.marche.it/"
        },
        {
            "regione": "Calabria",
            "ente": "Turismo Calabria",
            "url": "https://www.calabriaturismo.it/"
        }
    ]

    for site in sites:
        check_site(site["url"], site["regione"], site["ente"])

    print("Monitoraggio completato.")

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
import gspread
import json

# ====== CARICA FONTI ======
with open("sources.json", "r") as f:
    sites = json.load(f)
    
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

            if text and href and not href.startswith("javascript") and not href.startswith("#"):
                score = 0
                text_lower = text.lower()
            score = 0

            # ===== KEYWORD POSITIVE PESATE =====
            positive_keywords = {
                "bando": 5,
                "gara": 5,
                "affidamento": 5,
                "manifestazione di interesse": 4,
                "promozione territoriale": 4,
                "marketing territoriale": 4,
                "destination": 5,
                "wedding": 6,
                "incoming": 4,
                "turismo internazionale": 4,
                "brand territoriale": 4,
                "campagna": 3,
                "eventi": 3
            }

            for keyword, weight in positive_keywords.items():
                if keyword in text_lower:
                    score += weight

            # ===== KEYWORD NEGATIVE =====
            negative_keywords = [
                "microimprese",
                "pmi",
                "fondo perduto",
                "sostegno alle imprese",
                "voucher imprese",
                "contributo alle imprese"
            ]

            for bad_word in negative_keywords:
                if bad_word in text_lower:
                    score = 0
                    break


                if score >= 5 and href not in existing_urls:
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

    for site in sites:
        check_site(
            site["url"],
            site["regione"],
            site["ente"]
        )

    print("Monitoraggio completato.")

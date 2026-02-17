import requests
from bs4 import BeautifulSoup
from datetime import datetime

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Recupera il secret da GitHub Actions
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

# Converte stringa JSON in oggetto Python
creds_dict = json.loads(credentials_json)

# Imposta accesso Google Sheet
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Apri il foglio tramite ID
sheet = client.open_by_key("1MQ0mn4dTvAR4Ba72N_f0OTIlEFpyX6GxZGo9e2oaRI6c18cpW18wWyDv").sheet1
 check_site(url, regione, ente):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        titles = soup.find_all("a")[:10]  # prende i primi 10 link

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

                if score > 0:
                    results.append({
                        "regione": regione,
                        "ente": ente,
                        "titolo": text,
                        "url": href,
                        "score": score,
                        "data": datetime.today().strftime("%Y-%m-%d")
                    })
    # Scrive risultati nello Sheet
    for r in results:
        sheet.append_row([
            r["regione"],
            r["ente"],
            "Bando/Avviso",    # Tipo Documento
            r["titolo"],
            r["url"],
            r["data"],         # Data Pubblicazione
            "",                # Scadenza
            "",                # Budget stimato
            "",                # Compatibilità
            r["score"],        # Score calcolato
            "",                # Azione consigliata
            "",                # Email generata
            "Nuovo"            # Stato
        ])
        return results

    except Exception as e:
        print("Errore:", e)
        return []


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

    all_results = []

    for site in sites:
        results = check_site(site["url"], site["regione"], site["ente"])
        all_results.extend(results)

    print("Risultati trovati:")
    for r in all_results:
        print(r)

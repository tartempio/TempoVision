import urllib.request
from bs4 import BeautifulSoup
import re

TARGET_URL = "https://www.kelwatt.fr/fournisseurs/edf/tempo"
WEEKDAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
TEMPO_COLOURS = ("Rouge", "Blanc", "Bleu")

def fetch():
    req = urllib.request.Request(TARGET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

html = fetch()

def parse_tempo_page(html: str):
    results = {}
    soup = BeautifulSoup(html, "html.parser")

    days_in_order = []

    # 1. Parse Today and Tomorrow
    for text in ["Aujourd'hui", "Demain"]:
        el = soup.find(string=re.compile(text))
        if el:
            header = el.find_parent("div", class_=re.compile("card-header"))
            if header:
                day_p = header.find("p", class_=re.compile("text--xs"))
                if day_p:
                    date_str = day_p.get_text(strip=True).lower() # "dimanche 01 mars"
                    day_str = date_str.split(" ")[0]
                    if day_str in WEEKDAYS:
                        card = header.find_parent("div")
                        if card:
                            card_text = card.get_text(separator=" ", strip=True)
                            match = re.search(r"Tempo\s+(Bleu|Blanc|Rouge)", card_text, re.IGNORECASE)
                            color = match.group(1).capitalize() if match else None
                            if color:
                                results[date_str] = {"color": color, "probs": {}, "date": date_str}
                                days_in_order.append(date_str)

    # 2. Parse Predictions (Prévisions) for the next 5 days
    for card in soup.find_all("div", class_=lambda x: x and "card" in x):
        header = card.find("div", class_="card-score__header")
        if header:
            title_p = header.find("p", class_="card-score__header--title")
            if title_p:
                date_str = title_p.get_text(strip=True).lower()
                day_str = date_str.split(" ")[0]
                if day_str in WEEKDAYS and date_str not in results:
                    color = None
                    for strong in card.find_all("strong"):
                        color_text = strong.get_text(strip=True).capitalize()
                        if color_text in TEMPO_COLOURS:
                            color = color_text
                            break
                    
                    if color:
                        probs = {"Bleu": 0, "Blanc": 0, "Rouge": 0}
                        prob_bar = card.find("div", class_="probability-bar")
                        if prob_bar:
                            for div in prob_bar.find_all("div", title=True):
                                title = div.get("title", "")
                                match = re.search(r"(Bleu|Blanc|Rouge)\s*:\s*([\d,.]+)\s*%", title)
                                if match:
                                    p_color = match.group(1)
                                    prob_val = float(match.group(2).replace(",", "."))
                                    probs[p_color] = prob_val
    
                        results[date_str] = {"color": color, "probs": probs, "date": date_str}
                        days_in_order.append(date_str)

    # Now tag them with offset
    final_dict = {}
    for i, date_str in enumerate(days_in_order):
        offset_name = f"J_{i}" if i == 0 else f"J+{i}"
        final_dict[offset_name] = results[date_str]

    return final_dict

import pprint
pprint.pprint(parse_tempo_page(html))

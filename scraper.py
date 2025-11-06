import requests
from lxml import html
import csv
from time import sleep

HEADERS = {"User-Agent": "Mozilla/5.0"}
YEARS = range(2012, 2026)
CSV_FILE = "history.csv"

def scrape_year(year):
    url = f"https://www.beatlottery.co.uk/eurojackpot/draw-history/year/{year}"
    print(f"Lade Jahr {year} … ({url})")
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    tree = html.fromstring(resp.text)
    
    rows = tree.xpath('//tr[td/div[@class="results-ball-box"]]')
    print(f"  Gefundene Ziehungen Jahr {year}: {len(rows)}")
    
    results = []
    for row in rows:
        try:
            date_text = row.xpath('./td[2]/text()')[0].strip()
            spans = row.xpath('./td[4]/div/span')
            numbers = [int(s.text.strip()) for s in spans if s.text and s.text.strip().isdigit()]
            main_numbers = numbers[:5]
            euro_numbers = numbers[5:7]
            results.append([date_text] + main_numbers + euro_numbers)
        except Exception as e:
            print(f"  Fehler beim Parsen einer Zeile: {e}")
    return results

def main():
    all_results = []
    for year in YEARS:
        try:
            year_results = scrape_year(year)
            all_results.extend(year_results)
            sleep(1)  # freundlich zu Servern
        except Exception as e:
            print(f"Fehler beim Jahr {year}: {e}")
    
    # CSV schreiben
    header = ["Date", "Main1", "Main2", "Main3", "Main4", "Main5", "Euro1", "Euro2"]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_results)
    print(f"CSV '{CSV_FILE}' erstellt. JS-kompatibel!")

if __name__ == "__main__":
    main()

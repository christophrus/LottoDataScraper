import requests
from lxml import html
import csv
import re
from datetime import datetime, date
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


def parse_date(date_text):
    """Parse date strings and return a datetime.date.

    Expects the date in the CSV to be in format dd/mm/yyyy, but will try a
    few common alternatives as fallback.
    Returns None if parsing fails.
    """
    if not date_text:
        return None
    s = date_text.strip()
    # Normalize common separators
    s = s.replace('.', '/').replace('-', '/').strip()
    # Try dd/mm/YYYY first (the CSV format you mentioned)
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except Exception:
        pass

    # Other common formats
    fmts = ["%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%Y-%m-%d"]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue

    # Fallback: try to extract numbers (day, month, year)
    m = re.search(r"(\d{1,2})\D+(\d{1,2})\D+(\d{4})", s)
    if m:
        d, mth, y = m.group(1), m.group(2), m.group(3)
        try:
            return date(int(y), int(mth), int(d))
        except Exception:
            return None
    return None

def main():
    all_results = []
    for year in YEARS:
        try:
            year_results = scrape_year(year)
            all_results.extend(year_results)
            sleep(1)  # freundlich zu Servern
        except Exception as e:
            print(f"Fehler beim Jahr {year}: {e}")
    
    # Ergebnisse nach Datum sortieren (ältestes oben, neustes unten).
    # Wenn das Datum nicht geparst werden kann, legen wir es auf date.min
    # damit solche Zeilen oben erscheinen.
    try:
        all_results.sort(key=lambda r: parse_date(r[0]) or date.min)
    except Exception as e:
        print(f"Fehler beim Sortieren nach Datum: {e}")

    # CSV schreiben
    header = ["Date", "Main1", "Main2", "Main3", "Main4", "Main5", "Euro1", "Euro2"]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_results)
    print(f"CSV '{CSV_FILE}' erstellt. JS-kompatibel!")

if __name__ == "__main__":
    main()

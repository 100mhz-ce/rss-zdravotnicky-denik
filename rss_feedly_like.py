import feedparser
import csv
import datetime
import os
import time

FEED_URL = "https://www.zdravotnickydenik.cz/rss"
ARCHIVE_FILE = "archive.csv"
OUTPUT_FILE = "vypis_vcera.csv"

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# =========================
# 1) Načtení archivu
# =========================
known_ids = set()
archive_rows = []

if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            known_ids.add(row["ID"])
            archive_rows.append(row)

# =========================
# 2) Stažení RSS s retry
# =========================
feed = None
for attempt in range(3):
    feed = feedparser.parse(FEED_URL)
    if feed.entries:
        break
    time.sleep(5)

if not feed or not feed.entries:
    print("RSS feed se nepodařilo načíst.")
    exit(0)

# =========================
# 3) Zpracování nových článků
# =========================
for entry in feed.entries:
    entry_id = entry.get("id") or entry.get("link")
    if not entry_id or entry_id in known_ids:
        continue

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        published = datetime.date(
            entry.published_parsed.tm_year,
            entry.published_parsed.tm_mon,
            entry.published_parsed.tm_mday
        )
    else:
        published = today

    archive_rows.append({
        "ID": entry_id,
        "Datum": published.isoformat(),
        "Titulek": entry.title.strip(),
        "Popis": entry.get("summary", "").strip(),
        "Odkaz": entry.link
    })
    known_ids.add(entry_id)

# =========================
# 4) Uložení archivu
# =========================
with open(ARCHIVE_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["ID", "Datum", "Titulek", "Popis", "Odkaz"]
    )
    writer.writeheader()
    writer.writerows(archive_rows)

# =========================
# 5) Výpis včerejších článků
# =========================
vcera = [
    row for row in archive_rows
    if row["Datum"] == yesterday.isoformat()
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["Datum", "Titulek", "Popis", "Odkaz"]
    )
    writer.writeheader()
    writer.writerows(vcera)

print(f"Nalezeno včerejších článků: {len(vcera)}")

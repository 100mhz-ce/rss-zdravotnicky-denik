import feedparser
import csv
import datetime
import os

FEED_URL = "https://www.zdravotnickydenik.cz/rss"
ARCHIVE_FILE = "archive.csv"
OUTPUT_FILE = "vypis_vcera.csv"

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

known_ids = set()
archive_rows = []

if os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            known_ids.add(row[0])
            archive_rows.append(row)

feed = feedparser.parse(FEED_URL)

for entry in feed.entries:
    entry_id = entry.get("id") or entry.get("link")

    if entry_id in known_ids:
        continue

    if hasattr(entry, "published_parsed"):
        published = datetime.date(
            entry.published_parsed.tm_year,
            entry.published_parsed.tm_mon,
            entry.published_parsed.tm_mday
        )
    else:
        published = today

    archive_rows.append([
        entry_id,
        published.isoformat(),
        entry.title,
        entry.get("summary", ""),
        entry.link
    ])
    known_ids.add(entry_id)

with open(ARCHIVE_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "Datum", "Titulek", "Popis", "Odkaz"])
    writer.writerows(archive_rows)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Datum", "Titulek", "Popis", "Odkaz"])
    for row in archive_rows:
        if row[1] == yesterday.isoformat():
            writer.writerow(row[1:])

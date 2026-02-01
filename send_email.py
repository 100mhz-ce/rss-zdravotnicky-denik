import os
import csv
import smtplib
from email.message import EmailMessage
from datetime import date, timedelta

# --- Nastavení ---
CSV_FILE = "vypis_vcera.csv"
TO_EMAIL = "ranni.svodky@centrum.cz"

# --- SMTP ze Secrets ---
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = int(os.environ["SMTP_PORT"])

# --- Datum ---
yesterday = date.today() - timedelta(days=1)
date_str = yesterday.strftime("%d.%m.%Y")

# --- Načtení CSV ---
lines = []
with open(CSV_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, start=1):
        title = row.get("title") or row.get("Title") or row.get("nazev") or ""
        summary = row.get("summary") or row.get("Summary") or row.get("description") or ""
        link = row.get("link") or row.get("Link") or row.get("odkaz") or ""

        if not title and not link:
            continue

        lines.append(
            f"{i}) {title}\n"
            f"   {summary.strip()}\n"
            f"   {link}\n"
        )


# --- Email ---
msg = EmailMessage()
msg["From"] = SMTP_USER
msg["To"] = TO_EMAIL
msg["Subject"] = f"Ranní svodka – Zdravotnický deník ({date_str})"
msg.set_content(body)

# --- Odeslání ---
with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
    server.login(SMTP_USER, SMTP_PASS)
    server.send_message(msg)

print("Email úspěšně odeslán.")

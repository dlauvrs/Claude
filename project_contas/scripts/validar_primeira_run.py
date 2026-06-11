"""Vigia da primeira run: detecta linhas novas na planilha e queda de unread."""
import sys
import time

sys.path.insert(0, "scripts")
from google_client import gmail_service, sheets_service, sheet_id

ABAS = ["minas_sucata", "minas_japan", "daniel", "outros"]


def snapshot():
    svc = sheets_service()
    counts = {}
    for aba in ABAS:
        resp = svc.spreadsheets().values().get(
            spreadsheetId=sheet_id(), range=f"{aba}!A:A"
        ).execute()
        counts[aba] = max(0, len(resp.get("values", [])) - 1)
    unread = gmail_service().users().messages().list(
        userId="me", q="is:unread", maxResults=1
    ).execute().get("resultSizeEstimate", -1)
    return counts, unread


base_counts, base_unread = snapshot()
print(f"BASELINE linhas={base_counts} unread~{base_unread}", flush=True)

deadline = time.time() + 20 * 60
while time.time() < deadline:
    time.sleep(45)
    try:
        counts, unread = snapshot()
    except Exception as e:
        print(f"erro no poll (seguindo): {e}", flush=True)
        continue
    novas = {a: counts[a] - base_counts[a] for a in ABAS if counts[a] != base_counts[a]}
    if novas:
        print(f"PLANILHA MUDOU: linhas novas {novas} | unread~{unread} (era ~{base_unread})", flush=True)
        sys.exit(0)
print(f"TIMEOUT 20min sem mudanca na planilha. unread~{snapshot()[1]} (era ~{base_unread})", flush=True)
sys.exit(1)

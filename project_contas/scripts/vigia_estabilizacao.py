"""Acompanha a run de ingestão até estabilizar (unread e planilha param de mudar)."""
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


prev_counts, prev_unread = snapshot()
print(f"inicio: linhas={prev_counts} unread~{prev_unread}", flush=True)
estavel = 0
deadline = time.time() + 40 * 60

while time.time() < deadline:
    time.sleep(60)
    try:
        counts, unread = snapshot()
    except Exception as e:
        print(f"erro no poll (seguindo): {e}", flush=True)
        continue
    if counts != prev_counts or unread != prev_unread:
        delta = {a: counts[a] - prev_counts[a] for a in ABAS if counts[a] != prev_counts[a]}
        print(f"mudou: novas={delta} unread~{unread}", flush=True)
        prev_counts, prev_unread = counts, unread
        estavel = 0
    else:
        estavel += 1
        if estavel >= 4:
            print(f"ESTABILIZOU: linhas={counts} unread~{unread} — run provavelmente terminou", flush=True)
            sys.exit(0)
print("TIMEOUT 40min ainda mudando — backlog grande, run segue", flush=True)
sys.exit(0)

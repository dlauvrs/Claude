"""Detecta o proximo email que o agente enviar pro Daniel e imprime o assunto."""
import sys
import time

sys.path.insert(0, "scripts")
from google_client import gmail_service

svc = gmail_service()
QUERY = "in:sent to:daniellauvrs0@gmail.com newer_than:1d"

vistos = {m["id"] for m in svc.users().messages().list(
    userId="me", q=QUERY, maxResults=50
).execute().get("messages", [])}
print(f"monitorando enviados (baseline {len(vistos)})", flush=True)

deadline = time.time() + 25 * 60
while time.time() < deadline:
    time.sleep(30)
    try:
        msgs = svc.users().messages().list(userId="me", q=QUERY, maxResults=50).execute().get("messages", [])
    except Exception as e:
        print(f"erro no poll (seguindo): {e}", flush=True)
        continue
    novos = [m["id"] for m in msgs if m["id"] not in vistos]
    if novos:
        for mid in novos:
            d = svc.users().messages().get(
                userId="me", id=mid, format="metadata", metadataHeaders=["Subject", "To"]
            ).execute()
            hdrs = {h["name"]: h["value"] for h in d["payload"]["headers"]}
            print(f"EMAIL ENVIADO: {hdrs.get('Subject', '?')}", flush=True)
        sys.exit(0)
print("TIMEOUT 25min sem email enviado — investigar a sessao da routine", flush=True)
sys.exit(1)

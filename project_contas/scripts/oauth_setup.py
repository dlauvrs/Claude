"""
Script local one-shot para obter refresh_token de assistentepessoalcontas@gmail.com.
Roda uma vez, abre browser, captura authorization code, troca por refresh_token.
O refresh_token nunca expira (até ser revogado) e vai virar env var nas routines.

Uso:
    cd "/Users/daniellauvrs/Trabalho /Claude/project_contas"
    python3 -m venv .venv && source .venv/bin/activate
    pip install google-auth google-auth-oauthlib
    python scripts/oauth_setup.py
"""
import json
import os
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
]

CLIENT_SECRETS_PATH = Path(
    "/Users/daniellauvrs/Trabalho /Claude/Credenciais e Outros/oauth_client_project_contas.json"
)
OUTPUT_PATH = Path(
    "/Users/daniellauvrs/Trabalho /Claude/Credenciais e Outros/project_contas_token.json"
)


def main() -> None:
    if not CLIENT_SECRETS_PATH.exists():
        print(f"ERRO: nao achei {CLIENT_SECRETS_PATH}")
        print("Baixa o JSON do OAuth Client (Desktop app) no console.cloud.google.com")
        print("e salva nesse caminho.")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_PATH), SCOPES)
    print("Vai abrir o browser. Loga com assistentepessoalcontas@gmail.com e autoriza todos os escopos.")
    print("Se aparecer aviso de 'app nao verificado', clica em 'Advanced' -> 'Go to project_contas'.\n")
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        print("ERRO: nao recebi refresh_token. Revogue o app em myaccount.google.com/permissions e rode de novo.")
        sys.exit(1)

    payload = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "scopes": creds.scopes,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2))
    os.chmod(OUTPUT_PATH, 0o600)
    print(f"OK. Credenciais salvas em {OUTPUT_PATH}")
    print("\nAgora copia esses valores pras env vars da routine (claude.ai > Routines > Environment):")
    print(f"  GOOGLE_CLIENT_ID={creds.client_id}")
    print(f"  GOOGLE_CLIENT_SECRET={creds.client_secret}")
    print(f"  GOOGLE_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()

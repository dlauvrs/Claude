"""
Cliente Gmail+Sheets usado pelas 4 routines.
Le credenciais de env vars (GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN, SHEETS_ID).
Funcoes expostas: list_unread, get_message, mark_read, send_email,
read_sheet, append_row, update_row_by_id.

Uso dentro da routine (bash dentro da routine roda isso):
    python scripts/google_client.py list_unread
    python scripts/google_client.py send_email --to ... --subject ... --body-file ...
    python scripts/google_client.py read_sheet --aba minas_sucata
    python scripts/google_client.py append_row --aba daniel --json '{"descricao":"..."}'
    python scripts/google_client.py update_row_by_id --aba outros --id 42 --json '{"status":"pago"}'

Sempre imprime JSON puro pra stdout (facil de Claude parsear).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
]

SHEET_HEADERS = [
    "id", "tipo", "status", "descricao", "fornecedor_cliente", "valor",
    "vencimento", "data_pagamento", "categoria", "email_id", "pdf_drive_url",
    "linha_digitavel", "identificador_destino", "criado_em", "observacoes",
]


def get_credentials() -> Credentials:
    client_id = os.environ["GOOGLE_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
    refresh_token = os.environ["GOOGLE_REFRESH_TOKEN"]
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def gmail_service():
    return build("gmail", "v1", credentials=get_credentials(), cache_discovery=False)


def sheets_service():
    return build("sheets", "v4", credentials=get_credentials(), cache_discovery=False)


def sheet_id() -> str:
    return os.environ["SHEETS_ID"]


# ---------- Gmail ----------

def list_unread(max_results: int = 50) -> list[dict[str, Any]]:
    svc = gmail_service()
    resp = svc.users().messages().list(
        userId="me", q="is:unread -from:me", maxResults=max_results
    ).execute()
    return resp.get("messages", [])


def get_message(message_id: str) -> dict[str, Any]:
    svc = gmail_service()
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}

    def collect_parts(payload: dict[str, Any], acc: list[dict[str, Any]]) -> None:
        if "parts" in payload:
            for p in payload["parts"]:
                collect_parts(p, acc)
        else:
            acc.append(payload)

    parts: list[dict[str, Any]] = []
    collect_parts(msg["payload"], parts)

    text_plain = ""
    text_html = ""
    attachments = []
    for p in parts:
        mime = p.get("mimeType", "")
        body = p.get("body", {})
        data = body.get("data")
        filename = p.get("filename", "")
        if filename and body.get("attachmentId"):
            attachments.append({
                "filename": filename,
                "mime": mime,
                "attachment_id": body["attachmentId"],
                "size": body.get("size", 0),
            })
        elif mime == "text/plain" and data:
            text_plain += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        elif mime == "text/html" and data:
            text_html += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    return {
        "id": msg["id"],
        "thread_id": msg["threadId"],
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "subject": headers.get("subject", ""),
        "date": headers.get("date", ""),
        "snippet": msg.get("snippet", ""),
        "text_plain": text_plain,
        "text_html": text_html,
        "attachments": attachments,
        "label_ids": msg.get("labelIds", []),
    }


def get_attachment(message_id: str, attachment_id: str) -> bytes:
    svc = gmail_service()
    att = svc.users().messages().attachments().get(
        userId="me", messageId=message_id, id=attachment_id
    ).execute()
    return base64.urlsafe_b64decode(att["data"])


def mark_read(message_id: str) -> None:
    svc = gmail_service()
    svc.users().messages().modify(
        userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
    ).execute()


def add_label(message_id: str, label_id: str) -> None:
    svc = gmail_service()
    svc.users().messages().modify(
        userId="me", id=message_id, body={"addLabelIds": [label_id]}
    ).execute()


def trash_message(message_id: str) -> None:
    """Move pra lixeira do Gmail (recuperavel por 30 dias)."""
    svc = gmail_service()
    svc.users().messages().trash(userId="me", id=message_id).execute()


def get_or_create_label(name: str) -> str:
    svc = gmail_service()
    labels = svc.users().labels().list(userId="me").execute().get("labels", [])
    for lbl in labels:
        if lbl["name"] == name:
            return lbl["id"]
    created = svc.users().labels().create(
        userId="me",
        body={"name": name, "labelListVisibility": "labelShow", "messageListVisibility": "show"},
    ).execute()
    return created["id"]


def archive_with_label(message_id: str, label_name: str) -> None:
    """Tira da caixa de entrada (e de nao-lidos) e aplica etiqueta. Nada e deletado."""
    svc = gmail_service()
    label_id = get_or_create_label(label_name)
    svc.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX", "UNREAD"]},
    ).execute()


def send_email(to: str, subject: str, body: str, in_reply_to: str | None = None) -> str:
    svc = gmail_service()
    msg = MIMEText(body, "plain", "utf-8")
    msg["to"] = to
    subject_encoded = subject.encode("utf-8")
    msg["subject"] = "=?utf-8?B?" + base64.b64encode(subject_encoded).decode() + "?="
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    payload: dict[str, Any] = {"raw": raw}
    sent = svc.users().messages().send(userId="me", body=payload).execute()
    return sent["id"]


# ---------- Sheets ----------

DATE_COLUMNS = ("vencimento", "data_pagamento", "criado_em")


def _serial_to_iso(value: Any) -> Any:
    """Sheets devolve datas como serial (dias desde 1899-12-30) no UNFORMATTED_VALUE."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    if not 20000 <= value <= 80000:
        return value
    return (date(1899, 12, 30) + timedelta(days=int(value))).isoformat()


def read_sheet(aba: str) -> list[dict[str, Any]]:
    svc = sheets_service()
    rng = f"{aba}!A:O"
    resp = svc.spreadsheets().values().get(
        spreadsheetId=sheet_id(), range=rng, valueRenderOption="UNFORMATTED_VALUE"
    ).execute()
    values = resp.get("values", [])
    if not values:
        return []
    headers = values[0] if values else SHEET_HEADERS
    rows = []
    for v in values[1:]:
        row = {h: (v[i] if i < len(v) else "") for i, h in enumerate(headers)}
        for col in DATE_COLUMNS:
            if col in row:
                row[col] = _serial_to_iso(row[col])
        rows.append(row)
    return rows


def append_row(aba: str, data: dict[str, Any]) -> str:
    svc = sheets_service()
    existing = read_sheet(aba)
    next_id = (max((int(r.get("id", 0) or 0) for r in existing), default=0)) + 1
    data["id"] = next_id
    data.setdefault("criado_em", datetime.now().isoformat(timespec="seconds"))
    row = [data.get(h, "") for h in SHEET_HEADERS]
    svc.spreadsheets().values().append(
        spreadsheetId=sheet_id(),
        range=f"{aba}!A:O",
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()
    return str(next_id)


def update_row_by_id(aba: str, row_id: int, updates: dict[str, Any]) -> bool:
    svc = sheets_service()
    rng = f"{aba}!A:O"
    resp = svc.spreadsheets().values().get(
        spreadsheetId=sheet_id(), range=rng, valueRenderOption="UNFORMATTED_VALUE"
    ).execute()
    values = resp.get("values", [])
    if not values:
        return False
    headers = values[0]
    for idx, v in enumerate(values[1:], start=2):
        row = {h: (v[i] if i < len(v) else "") for i, h in enumerate(headers)}
        if str(row.get("id", "")) == str(row_id):
            for k, val in updates.items():
                row[k] = val
            new_row = [row.get(h, "") for h in headers]
            svc.spreadsheets().values().update(
                spreadsheetId=sheet_id(),
                range=f"{aba}!A{idx}:O{idx}",
                valueInputOption="USER_ENTERED",
                body={"values": [new_row]},
            ).execute()
            return True
    return False


# ---------- CLI ----------

def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list_unread").add_argument("--max", type=int, default=50)

    p_get = sub.add_parser("get_message")
    p_get.add_argument("--id", required=True)

    p_att = sub.add_parser("get_attachment")
    p_att.add_argument("--message-id", required=True)
    p_att.add_argument("--attachment-id", required=True)
    p_att.add_argument("--out", required=True, help="caminho pra salvar o anexo")

    p_mark = sub.add_parser("mark_read")
    p_mark.add_argument("--id", required=True)

    p_trash = sub.add_parser("trash")
    p_trash.add_argument("--id", required=True)

    p_arch = sub.add_parser("archive")
    p_arch.add_argument("--id", required=True)
    p_arch.add_argument("--label", required=True)

    p_send = sub.add_parser("send_email")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--body-file", required=True)
    p_send.add_argument("--in-reply-to", default=None)

    p_read = sub.add_parser("read_sheet")
    p_read.add_argument("--aba", required=True)

    p_app = sub.add_parser("append_row")
    p_app.add_argument("--aba", required=True)
    p_app.add_argument("--json", required=True, help="JSON com campos da linha")

    p_upd = sub.add_parser("update_row_by_id")
    p_upd.add_argument("--aba", required=True)
    p_upd.add_argument("--id", type=int, required=True)
    p_upd.add_argument("--json", required=True, help="JSON com campos a atualizar")

    args = parser.parse_args()

    if args.cmd == "list_unread":
        print(json.dumps(list_unread(args.max), ensure_ascii=False))
    elif args.cmd == "get_message":
        print(json.dumps(get_message(args.id), ensure_ascii=False))
    elif args.cmd == "get_attachment":
        data = get_attachment(args.message_id, args.attachment_id)
        with open(args.out, "wb") as f:
            f.write(data)
        print(json.dumps({"saved": args.out, "bytes": len(data)}))
    elif args.cmd == "mark_read":
        mark_read(args.id)
        print(json.dumps({"ok": True}))
    elif args.cmd == "trash":
        trash_message(args.id)
        print(json.dumps({"trashed": True}))
    elif args.cmd == "archive":
        archive_with_label(args.id, args.label)
        print(json.dumps({"archived": True, "label": args.label}))
    elif args.cmd == "send_email":
        with open(args.body_file, "r", encoding="utf-8") as f:
            body = f.read()
        msg_id = send_email(args.to, args.subject, body, args.in_reply_to)
        print(json.dumps({"message_id": msg_id}))
    elif args.cmd == "read_sheet":
        print(json.dumps(read_sheet(args.aba), ensure_ascii=False, default=str))
    elif args.cmd == "append_row":
        data = json.loads(args.json)
        new_id = append_row(args.aba, data)
        print(json.dumps({"id": new_id}))
    elif args.cmd == "update_row_by_id":
        updates = json.loads(args.json)
        ok = update_row_by_id(args.aba, args.id, updates)
        print(json.dumps({"updated": ok}))


if __name__ == "__main__":
    main()

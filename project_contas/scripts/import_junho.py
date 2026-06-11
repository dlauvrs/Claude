"""Importa JUNHO 2026 da planilha manual do Daniel pras abas do agente.

Regras acordadas (2026-06-10):
- "Minas Sucata" -> minas_sucata | "Brum e Dias" -> minas_japan (razao social) |
  "Pessoal" -> separar por contexto; sem pista -> outros com identificador "revisar"
- Obs com token OK -> pago; senao aberto. Nunca inventar valor nem data de pagamento.
- Valor vazio -> "" + obs "valor a confirmar"; se MAIO 2026 tem a mesma descricao
  com valor, anexa "ref maio/2026: R$ X" SO NA OBSERVACAO.
- Dedup contra as 4 abas por (vencimento, valor).
"""
import re
import sys
import unicodedata
from datetime import datetime

import pandas as pd

sys.path.insert(0, "scripts")
from google_client import read_sheet, sheets_service, sheet_id, SHEET_HEADERS

XLSX = "/Users/daniellauvrs/Downloads/CONTAS A PAGAR.xlsx"
HOJE = "2026-06-10"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def carregar_aba(nome):
    df = pd.read_excel(XLSX, sheet_name=nome, header=None)
    linhas = []
    for _, r in df.iloc[6:].iterrows():
        desc = r[1]
        if pd.isna(desc) or not str(desc).strip():
            continue
        venc = r[3]
        venc_iso = venc.strftime("%Y-%m-%d") if isinstance(venc, datetime) else ""
        valor = r[4]
        valor = round(float(valor), 2) if pd.notna(valor) and isinstance(valor, (int, float)) and valor > 0 else None
        obs1 = "" if pd.isna(r[5]) else str(r[5]).strip()
        obs2 = "" if (len(r) < 7 or pd.isna(r[6])) else str(r[6]).strip()
        linhas.append({
            "descricao": str(desc).strip(),
            "empresa": "" if pd.isna(r[2]) else str(r[2]).strip(),
            "vencimento": venc_iso,
            "valor": valor,
            "obs1": obs1,
            "obs2": obs2,
        })
    return linhas


def categoria_de(desc):
    d = desc.lower()
    pares = [
        ("aluguel", "aluguel"), ("cart", "cartao"), ("cemig", "energia"), ("kw minas", "energia"),
        ("copasa", "agua"), ("emprest", "emprestimo"), ("financiamento", "financiamento"),
        ("folha", "folha"), ("fgts", "imposto"), ("inss", "imposto"), ("irrf", "imposto"),
        ("simples", "imposto"), ("iptu", "imposto"), ("ipva", "imposto"), ("icms", "imposto"),
        ("imposto de renda", "imposto"), ("e-social", "imposto"), ("seguro", "seguro"),
        ("unimed", "saude"), ("vivo", "telefonia"), ("claro", "telefonia"), ("condominio", "condominio"),
        ("colegio", "educacao"), ("escolar", "educacao"), ("formatura", "educacao"),
        ("padaria", "alimentacao"), ("refeic", "alimentacao"), ("restaurante", "alimentacao"),
        ("passagens", "transporte"), ("transportadora", "frete"), ("contabilidade", "servicos"),
    ]
    for chave, cat in pares:
        if chave in d:
            return cat
    return "geral"


junho = carregar_aba("JUNHO 2026")
maio = carregar_aba("MAIO 2026")
ref_maio = {}
for m in maio:
    if m["valor"]:
        ref_maio.setdefault(norm(m["descricao"]), m["valor"])

# dedup: chaves (venc, valor) das 4 abas atuais
existentes = set()
for aba in ["minas_sucata", "minas_japan", "daniel", "outros"]:
    for r in read_sheet(aba):
        venc, val = r.get("vencimento", ""), r.get("valor", "")
        try:
            existentes.add((str(venc), round(float(val), 2)))
        except (TypeError, ValueError):
            pass

novas = {"minas_sucata": [], "minas_japan": [], "daniel": [], "outros": []}
puladas, revisar = [], []

for c in junho:
    obs1_up = c["obs1"].upper()
    pago = bool(re.match(r"^\s*OK\b", obs1_up))
    status = "pago" if pago else "aberto"

    emp = norm(c["empresa"])
    pistas = f"{c['descricao']} {c['obs1']} {c['obs2']}".lower()
    identificador = "planilha manual"
    if emp == "minassucata":
        aba = "minas_sucata"
    elif emp in ("brumedias", "brumdias"):
        aba = "minas_japan"
        identificador = "razao social brum e dias"
    elif emp == "pessoal":
        if "caio" in pistas:
            aba, identificador = "outros", "caio"
        elif "lucas" in pistas:
            aba, identificador = "outros", "revisar"
            revisar.append(c["descricao"] + " — Lucas: Daniel ou Caio? (conflito escola Vimasa x Coleguium)")
        elif "condominio" in pistas:
            aba, identificador = "outros", "revisar"
            revisar.append(c["descricao"] + " — condomínio de quem?")
        else:
            aba, identificador = "outros", "revisar"
            revisar.append(c["descricao"] + " — Pessoal sem pista: Daniel ou Caio?")
    else:
        aba, identificador = "outros", "revisar"
        revisar.append(c["descricao"] + f" — empresa desconhecida: '{c['empresa']}'")

    if c["valor"] and (c["vencimento"], c["valor"]) in existentes:
        puladas.append(f"{c['descricao']} (R$ {c['valor']} venc {c['vencimento']}) — já estava na planilha do agente")
        continue

    obs_parts = ["importado da planilha manual 2026-06-10"]
    if c["obs1"] and not re.match(r"^\s*OK\s*$", obs1_up):
        obs_parts.append(f"obs original: {c['obs1']}")
    if c["obs2"]:
        obs_parts.append(c["obs2"])
    if pago:
        obs_parts.append("pago (data nao registrada na planilha manual)")
    if not c["valor"]:
        obs_parts.append("valor a confirmar quando chegar boleto")
        ref = ref_maio.get(norm(c["descricao"]))
        if ref:
            obs_parts.append(f"ref maio/2026: R$ {ref:.2f}")
    if "debito" in pistas and "automatico" in pistas.replace("á", "a").replace("é", "e") and not pago and c["vencimento"] <= HOJE:
        obs_parts.append("debito automatico — confirmar se debitou")

    novas[aba].append({
        "tipo": "pagar",
        "status": status,
        "descricao": c["descricao"],
        "fornecedor_cliente": "",
        "valor": c["valor"] if c["valor"] else "",
        "vencimento": c["vencimento"],
        "data_pagamento": "",
        "categoria": categoria_de(c["descricao"]),
        "email_id": "",
        "identificador_destino": identificador,
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "observacoes": " | ".join(obs_parts),
    })

svc = sheets_service()
for aba, rows in novas.items():
    if not rows:
        continue
    atuais = read_sheet(aba)
    ids_num = []
    for r in atuais:
        try:
            ids_num.append(int(r.get("id")))
        except (TypeError, ValueError):
            pass
    next_id = max(ids_num, default=0) + 1
    payload = []
    for i, r in enumerate(rows):
        r["id"] = next_id + i
        payload.append([r.get(h, "") for h in SHEET_HEADERS])
    svc.spreadsheets().values().append(
        spreadsheetId=sheet_id(), range=f"{aba}!A:O",
        valueInputOption="USER_ENTERED", body={"values": payload},
    ).execute()

print("=== IMPORT JUNHO 2026 ===")
for aba, rows in novas.items():
    ab = sum(1 for r in rows if r["status"] == "aberto")
    pg = len(rows) - ab
    print(f"{aba}: {len(rows)} importadas ({ab} abertas, {pg} pagas)")
print(f"\nPULADAS (duplicatas): {len(puladas)}")
for p in puladas:
    print(" -", p)
print(f"\nREVISAR ({len(revisar)}):")
for r in revisar:
    print(" -", r)

# Routine: Brief da manhã (8h, dias úteis — seg a sex)

Você é o agente financeiro do Daniel. Sua função nesta execução: enviar o resumo de contas da manhã. Trabalhe em português brasileiro.

## Setup

```bash
export TZ=America/Sao_Paulo
HOJE=$(date +%F)
DIA_SEMANA=$(date +%u)   # 1=segunda ... 5=sexta
pip install -q google-auth google-api-python-client 2>/dev/null
```

Env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `SHEETS_ID`, `GMAIL_DONO`.

## Fluxo

0. **Antes de tudo**: processe os emails não lidos seguindo `project_contas/routines/1_ingestao.md` — assim o resumo parte de dados frescos (contas que chegaram de madrugada, confirmações que o Daniel mandou ontem à noite).
1. Leia as 4 abas: `python project_contas/scripts/google_client.py read_sheet --aba {minas_sucata|minas_japan|daniel|outros}`. Ignore linhas com status `descartada` ou `movida`.
2. Separe as contas com `status` aberto em: **ATRASADAS** (vencimento < hoje), **HOJE** (= hoje), **SEMANA** (até domingo — usada só na segunda).
3. Monte o email conforme o dia da semana (abaixo) e envie para `$GMAIL_DONO`.

## REGRA DE FORMATO OBRIGATÓRIA — agrupamento por empresa

Em TODA seção do email, as contas são agrupadas por categoria, SEMPRE nesta ordem e com estes cabeçalhos, incluindo as categorias vazias (escrever "— nada"):

```
🏭 MINAS SUCATA — R$ {total} ({n} contas)
- {vence DD/MM} {descricao} — R$ {valor}
🚗 MINAS JAPAN — R$ {total} ({n} contas)
- ...
👤 DANIEL — R$ {total} ({n} contas)
- ...
📦 OUTROS (Caio, condomínio etc) — R$ {total} ({n} contas)
- ...
```

Nunca misture empresas numa lista única. O Daniel precisa bater o olho e saber o que é de cada empresa.

## Terça a sexta — brief do DIA

Assunto: `☀️ Contas de hoje, {dia da semana} {DD/MM} — R$ {total do dia}`

```
Bom dia, Daniel!

⚠️ ATRASADAS — R$ {total}    ← só se houver, agrupadas por empresa
{blocos por empresa}

📅 VENCEM HOJE — R$ {total}
{blocos por empresa}

🔭 Amanhã: {n} contas, R$ {total} (maior: {descricao} R$ {valor})

💡 {1-2 frases suas: o que merece atenção hoje, conta atípica,
concentração. Específico e com números, nunca filler.}
```

Se não houver NADA vencendo hoje nem atrasado: email curto confirmando ("✅ Nada vence hoje") + próximo vencimento de cada empresa que tiver algo em aberto.

## Segunda-feira — brief da SEMANA + dia

Assunto: `📋 Contas da semana — {DD/MM} a {DD/MM}`

```
Bom dia, Daniel! Resumo da semana:

⚠️ ATRASADAS — R$ {total}    ← só se houver, agrupadas por empresa
{blocos por empresa}

📅 HOJE, segunda — R$ {total}
{blocos por empresa}

📅 RESTO DA SEMANA (dia a dia, só dias com contas)
Terça {DD/MM} — R$ {total}: {lista curta com [empresa] em cada item}
Quarta {DD/MM} — nada
...

💰 TOTAIS DA SEMANA POR EMPRESA
🏭 Minas Sucata: R$ X ({n} contas)
🚗 Minas Japan: R$ Y ({n} contas)
👤 Daniel: R$ Z ({n} contas)
📦 Outros: R$ W ({n} contas)
TOTAL: R$ T

📊 LEITURA DA SEMANA
{2-4 frases SUAS, específicas e com números: dia mais pesado,
comparação com a semana anterior (total pago), contas atípicas vs
recorrente, concentrações. Se houver atrasadas, cobre resolução.}
```

## Regras

- Valores formato BR (R$ 1.234,56). Dentro de cada empresa, ordene por valor decrescente.
- Contas sem valor cadastrado: mostre "R$ ?" e a observação de referência se houver (ex. "ref maio: R$ 118,90") — NUNCA invente valor.
- Não repita a lista inteira da semana de terça a sexta — o panorama semanal é só na segunda.

# Routine: Lembrete da tarde (16h, todos os dias)

Você é o agente financeiro do Daniel. Sua função nesta execução: lembrar o que vence HOJE e pedir confirmação do que já foi pago. Trabalhe em português brasileiro.

## Setup

```bash
export TZ=America/Sao_Paulo
HOJE=$(date +%F)
pip install -q google-auth google-api-python-client 2>/dev/null
```

Env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `SHEETS_ID`, `GMAIL_DONO`.

## Fluxo

0. **Antes de tudo**: processe os emails não lidos seguindo `project_contas/routines/1_ingestao.md` — uma conta que chegou às 14h precisa aparecer neste lembrete, e uma confirmação de pagamento da manhã não pode ser cobrada de novo.
1. Leia as 4 abas (`read_sheet` via `project_contas/scripts/google_client.py`).
2. Filtre contas com `status` aberto e:
   - **VENCEM HOJE** (vencimento = hoje)
   - **ATRASADAS** (vencimento < hoje)
3. Envie email para `$GMAIL_DONO`.

## Caso 1: há contas vencendo hoje e/ou atrasadas

Assunto: `⏰ {n} contas vencem hoje — R$ {total}`

**FORMATO OBRIGATÓRIO: agrupar por empresa** (sempre nesta ordem: Minas Sucata, Minas Japan, Daniel, Outros; pule empresa sem contas neste email). A numeração é GLOBAL e contínua através dos grupos — é ela que o Daniel usa pra responder "paguei a 3".

```
Boa tarde! Checklist de pagamento de hoje:

VENCEM HOJE — R$ {total}:

🏭 MINAS SUCATA (R$ {subtotal})
1. {descricao} — R$ {valor}
   {linha digitável, se houver}
2. {descricao} — R$ {valor}

🚗 MINAS JAPAN (R$ {subtotal})
3. {descricao} — R$ {valor}

👤 DANIEL (R$ {subtotal})
4. {descricao} — R$ {valor}

📦 OUTROS (R$ {subtotal})
5. {descricao} — R$ {valor}

AINDA ABERTAS DE DIAS ANTERIORES — R$ {total}:    ← só se houver,
mesmo agrupamento por empresa, numeração continuando (6, 7...)

👉 Me responde esse email dizendo o que você já pagou (pode ser
do seu jeito: "paguei a 1 e a 3" ou "cemig paga, condomínio amanhã")
que eu atualizo a planilha. O que ficar em aberto eu cobro de novo
no fechamento das 19h.
```

Inclua a linha digitável logo abaixo da conta quando existir — economiza o Daniel de abrir o boleto.

## Caso 2: nada vence hoje e nada atrasado

Assunto: `✅ Nada vence hoje`

Email de 2-3 linhas no máximo: confirme que não há nada para hoje e diga qual é o próximo vencimento ("Próxima conta: {descricao}, R$ {valor}, {dia da semana} {DD/MM}").

## Envios por categoria (depois do consolidado)

Leia `python project_contas/scripts/google_client.py get_config --chave destinatarios_json`. Para CADA categoria em `por_categoria` com destinatários:
- Monte o MESMO checklist contendo APENAS as contas daquela categoria, com numeração própria começando em 1.
- Assunto: `⏰ {Empresa}: {n} contas vencem hoje — R$ {total}` (ou `✅ {Empresa}: nada vence hoje`).
- Adapte o rodapé: "Me responde esse email dizendo o que já foi pago que eu atualizo a planilha."
- Envie para cada endereço da lista.

O consolidado completo vai SEMPRE para `consolidado` (o Daniel). Os envios por categoria são adicionais.

## Regras

- Numere as contas (1, 2, 3...) — facilita o Daniel responder "paguei a 1 e a 2".
- Ordene: atrasadas mais antigas primeiro, depois as de hoje por valor decrescente.
- Não repita a "leitura da semana" — este email é um checklist objetivo, não um relatório.
- IMPORTANTE: a numeração de cada email é independente (consolidado tem a sua; cada email por empresa tem a sua própria). Quem interpreta as respostas (a ingestão) usa a thread do email respondido pra saber qual numeração vale.

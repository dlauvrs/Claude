# Routine: Fechamento do dia (19h, todos os dias)

Você é o agente financeiro do Daniel. Sua função nesta execução: fechar o dia — o que foi pago, o que ficou aberto, o que vem pela frente. Trabalhe em português brasileiro.

## Setup

```bash
export TZ=America/Sao_Paulo
HOJE=$(date +%F)
AMANHA=$(date -d "+1 day" +%F 2>/dev/null || date -v+1d +%F)
pip install -q google-auth google-api-python-client 2>/dev/null
```

Env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`, `SHEETS_ID`, `GMAIL_DONO`.

## Fluxo

0. **Antes de tudo**: processe os emails não lidos seguindo `project_contas/routines/1_ingestao.md` — em especial as respostas do Daniel ao lembrete das 16h confirmando pagamentos. Sem este passo, o fechamento cobraria contas que ele já confirmou.
1. Leia as 4 abas (`read_sheet` via `project_contas/scripts/google_client.py`).
2. Calcule:
   - **PAGAS HOJE**: status pago e data_pagamento = hoje
   - **FICARAM ABERTAS**: status aberto e vencimento <= hoje (venciam hoje ou antes e não foram confirmadas)
   - **AMANHÃ**: status aberto, vencimento = amanhã
   - **PRÓXIMOS 7 DIAS**: status aberto, vencimento entre depois de amanhã e hoje+7
3. Envie email para `$GMAIL_DONO` com assunto `🌙 Fechamento {DD/MM} — {frase curta do estado}` (ex.: "tudo pago", "2 ficaram abertas", "dia tranquilo").

## Formato do email

**FORMATO OBRIGATÓRIO: dentro de cada seção, agrupar por empresa** (ordem fixa: 🏭 Minas Sucata, 🚗 Minas Japan, 👤 Daniel, 📦 Outros; mostre subtotal por empresa e omita empresa sem itens naquela seção).

```
Fechamento de hoje, {dia da semana} {DD/MM}:

✅ PAGAS HOJE — R$ {total}
🏭 MINAS SUCATA (R$ {subtotal})
- {descricao} — R$ {valor}
🚗 MINAS JAPAN (R$ {subtotal})
- {descricao} — R$ {valor}
👤 DANIEL / 📦 OUTROS idem
(ou "Nenhum pagamento registrado hoje." — e se algo venceu hoje
sem confirmação, pergunte se ele esqueceu de confirmar ou de pagar)

⚠️ FICARAM ABERTAS — R$ {total}    ← só se houver, mesmo agrupamento
🏭 MINAS SUCATA (R$ {subtotal})
- {vencia DD/MM} {descricao} — R$ {valor}
...
{Se algo está aberto há 2+ dias, escale o tom: pergunte se quer
manter, se já pagou e esqueceu de confirmar, ou se há algum problema
com essa conta.}

📅 AMANHÃ ({dia da semana}) — R$ {total}, agrupado por empresa
(ou "Nada vence amanhã.")

🔭 PRÓXIMOS 7 DIAS — R$ {total} em {n} contas
Por empresa: 🏭 R$ X ({n}) | 🚗 R$ Y ({n}) | 👤 R$ Z ({n}) | 📦 R$ W ({n})
{Depois, resumo compacto por dia, só dias com contas: "Qui 13/06:
R$ 2.340 (3 contas, maior: aluguel Japan R$ 1.500)"}

💡 {1-3 frases SUAS: o dia foi bom ou ruim? A semana que vem começa
pesada? Tem concentração de vencimento chegando? Alguma conta
recorrente ainda não chegou este mês (ex.: "a CEMIG da Rio Pomba
costuma chegar até dia 12 e ainda não veio")? Seja específico.}
```

## Envios por categoria (depois do consolidado)

Leia `python project_contas/scripts/google_client.py get_config --chave destinatarios_json`. Para CADA categoria em `por_categoria` com destinatários:
- Monte o MESMO fechamento contendo APENAS as contas daquela categoria (pagas hoje, ficaram abertas, amanhã, próximos 7 dias — tudo só daquela empresa).
- Assunto: `🌙 {Empresa} — fechamento {DD/MM} — {frase curta}`.
- A observação 💡 deve falar só daquela empresa.
- Envie para cada endereço da lista. Se o dia da empresa foi 100% limpo, versão mínima.

O consolidado completo vai SEMPRE para `consolidado` (o Daniel). Os envios por categoria são adicionais.

## Regras

- Se o dia foi 100% limpo (nada pago porque nada vencia, nada aberto), mande versão mínima de 3-4 linhas com o panorama de amanhã e dos próximos dias.
- Valores formato BR.
- A observação final 💡 deve trazer informação que o Daniel ainda não tem — antecipação, padrão, ausência estranha. Nunca filler.

"""
Agente API — ver docs/design.md, seções 3.2 a 3.5.

Hospedado no Render (free web service). Expõe:
- Endpoint de ingestão, chamado pelo Serviço de Triagem quando encontra um
  e-mail relevante (autenticado via AGENT_WEBHOOK_TOKEN).
- Endpoint de chat, para conversar com o Agente Conversacional (coach).

TODO: montar a app FastAPI com esses dois endpoints.
TODO: acionar o pipeline fixo (extração -> categorização -> validação) na ingestão.
TODO: rotear perguntas de chat para o Agente Conversacional (agents/coach.py).
"""

from fastapi import FastAPI

app = FastAPI(title="FinCoach Agent API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# TODO: POST /ingest — recebe e-mail do Serviço de Triagem, aciona o pipeline fixo.
# TODO: POST /chat — recebe pergunta do usuário, aciona o Agente Conversacional.

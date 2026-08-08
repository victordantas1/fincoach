"""
Agente Conversacional (coach) — ver docs/design.md, seção 3.5.

Orquestrador dinâmico: usa como ferramentas a consulta ao MongoDB (dados
estruturados) e a busca na memória RAG (Atlas Vector Search). Acionado em
conversa direta com o usuário e em escalonamentos do Agente de Validação.

TODO: definir o teto máximo de passos (tool-calls) por tarefa — ver
docs/design.md, seção 4, "Mitigações de engenharia necessárias".
"""


def answer(question: str) -> str:
    """Responde a uma pergunta do usuário usando as ferramentas disponíveis."""
    raise NotImplementedError


def generate_proactive_insight() -> str:
    """Gera um insight proativo (ex: resumo mensal) sem pergunta do usuário."""
    raise NotImplementedError

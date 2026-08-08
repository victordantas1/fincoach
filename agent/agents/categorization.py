"""
Agente de Categorização — ver docs/design.md, seção 3.2.

Classifica cada transação numa categoria, usando RAG sobre categorizações
anteriores do próprio usuário para manter consistência ao longo do tempo.
"""


def categorize_transaction(transaction: dict) -> dict:
    """Retorna a transação com a categoria atribuída."""
    raise NotImplementedError

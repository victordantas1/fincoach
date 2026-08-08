"""
Agente de Extração — ver docs/design.md, seção 3.2.

Lê o PDF/corpo do e-mail e extrai transações brutas (data, estabelecimento,
valor, parcela quando aplicável). Usa LLM (não parser rígido por banco) —
deve funcionar razoavelmente bem mesmo para bancos sem template dedicado.
"""


def extract_transactions(document_content: bytes | str) -> list[dict]:
    """Retorna uma lista de transações brutas extraídas do documento."""
    raise NotImplementedError

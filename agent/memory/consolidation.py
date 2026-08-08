"""
Consolidação de Memória de Longo Prazo — ver docs/design.md, seção 3.4.

Processo periódico (não por transação) que consolida padrões a partir do
histórico bruto e grava os embeddings correspondentes via Atlas Vector Search.
"""


def consolidate() -> None:
    """Roda a consolidação periódica da memória de longo prazo."""
    raise NotImplementedError

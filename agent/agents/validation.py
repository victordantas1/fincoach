"""
Agente de Validação — ver docs/design.md, seção 3.2.

Sinaliza duplicatas, valores fora do padrão histórico, ou dados malformados.
Casos sinalizados aqui são o gatilho para escalar ao Agente Conversacional.
"""


def validate_transaction(transaction: dict) -> dict:
    """Retorna a transação com flags de validação (ex: is_anomaly, is_duplicate)."""
    raise NotImplementedError

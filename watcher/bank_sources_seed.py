"""
Script utilitário para popular/atualizar a coleção `bank_sources` no MongoDB.

Ver docs/design.md, seção 3.2.1 — adicionar um banco novo é inserir/atualizar
um documento aqui, sem alterar o código do watcher.

Exemplo de uso: python -m watcher.bank_sources_seed
"""

BANK_SOURCES = [
    {
        "bank_id": "nubank",
        "sender_patterns": ["@nubank.com.br"],
        "subject_patterns": ["fatura", "extrato"],
        "active": True,
    },
    # Exemplo de como adicionar um novo banco no futuro:
    # {
    #     "bank_id": "itau",
    #     "sender_patterns": ["@itau.com.br"],
    #     "subject_patterns": ["fatura", "extrato mensal"],
    #     "active": True,
    # },
]


def seed() -> None:
    """Insere/atualiza os documentos de BANK_SOURCES na coleção bank_sources."""
    raise NotImplementedError


if __name__ == "__main__":
    seed()

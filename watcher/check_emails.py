"""
Serviço de Triagem (Watcher) — ver docs/design.md, seção 3.1 e 3.2.1.

Executado diariamente via GitHub Actions (.github/workflows/watcher.yml).

Responsabilidades:
1. Carregar o registro de bancos monitorados (coleção `bank_sources` no MongoDB).
2. Consultar a API do Gmail (escopo `gmail.readonly`) filtrando por
   sender_patterns / subject_patterns de cada banco ativo.
3. Ignorar e-mails cujo message ID já esteja registrado como processado
   (idempotência — ver coleção `processed_emails`).
4. Para cada match novo, enviar o conteúdo (corpo + anexo) via POST
   autenticado (AGENT_WEBHOOK_TOKEN) para o endpoint de ingestão do
   Agente API hospedado no Render.

TODO: implementar autenticação OAuth do Gmail (leitura de credenciais via
GOOGLE_OAUTH_CREDENTIALS_PATH).
TODO: implementar a consulta e o filtro por bank_sources.
TODO: implementar o registro de idempotência em processed_emails.
TODO: implementar a chamada HTTP autenticada para o Agente API.
"""


def load_active_bank_sources() -> list[dict]:
    """Carrega os bancos monitorados e ativos a partir do MongoDB."""
    raise NotImplementedError


def find_new_matching_emails(bank_sources: list[dict]) -> list[dict]:
    """Consulta o Gmail e retorna e-mails novos que batem com algum banco monitorado."""
    raise NotImplementedError


def forward_to_agent(email: dict) -> None:
    """Envia o e-mail encontrado para o endpoint de ingestão do Agente API."""
    raise NotImplementedError


def main() -> None:
    bank_sources = load_active_bank_sources()
    new_emails = find_new_matching_emails(bank_sources)
    for email in new_emails:
        forward_to_agent(email)


if __name__ == "__main__":
    main()

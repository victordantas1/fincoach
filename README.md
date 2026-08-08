# FinCoach

Agente de coach financeiro pessoal com memória de longo prazo — monitora faturas e extratos bancários recebidos por e-mail, estrutura e categoriza as transações automaticamente, e conversa sobre insights financeiros com base num histórico consolidado.

Projeto de portfólio focado em orquestração multi-agente: um pipeline determinístico cuida da parte repetitiva (extração, categorização, validação), enquanto um agente conversacional dinâmico atua como orquestrador sobre os dados já estruturados e a memória de longo prazo.

Ver [docs/design.md](docs/design.md) para a arquitetura completa.

## Status

🚧 Em construção — Fase 1 (Ingestão + Estruturação).

## Stack

- Python
- Google Gemini API (free tier) + OpenRouter (fallback)
- MongoDB Atlas (dados estruturados + Atlas Vector Search para memória)
- Google Drive (armazenamento de documentos originais)
- GitHub Actions (serviço de triagem agendado)
- Render (hospedagem do agente)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # preencher com suas credenciais
```

## Licença

MIT — ver [LICENSE](LICENSE).

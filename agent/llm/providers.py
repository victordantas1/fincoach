"""
Estratégia de LLM com fallback — ver docs/design.md, seção 4.

Caminho primário: Gemini API (free tier).
Fallback: OpenRouter (free tier, modelos abertos) quando o Gemini retornar 429.

TODO: implementar chamada ao Gemini (google-generativeai) com backoff exponencial.
TODO: implementar fallback para OpenRouter (client compatível com OpenAI) em caso
de 429 esgotado no Gemini.
TODO: implementar teto de passos/tool-calls por tarefa (rate limiting interno).
"""


def call_llm(prompt: str, **kwargs) -> str:
    """Chama o LLM primário (Gemini); cai para o OpenRouter em caso de rate limit."""
    raise NotImplementedError

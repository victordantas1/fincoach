# Coach Financeiro com Memória de Longo Prazo — Documento de Design

**Status:** Draft aprovado em brainstorming — pronto para virar plano de implementação
**Data:** 2026-08-08
**Objetivo do projeto:** Peça de portfólio para vagas de pesquisa/indústria em IA (ex: Anthropic, DeepMind), com foco em orquestração multi-agente aplicada a um problema real e de uso diário.

---

## 1. Visão Geral

Um sistema multi-agente que monitora e-mails de bancos (começando pelo Nubank), estrutura faturas e extratos automaticamente, guarda um histórico organizado (dados + documentos originais), constrói uma memória de longo prazo sobre os padrões financeiros do usuário, e permite conversar com um agente "coach" que responde perguntas e gera insights proativos sobre as finanças pessoais.

O projeto foi desenhado para custar **$0** de operação, usando exclusivamente tiers gratuitos de APIs e serviços de nuvem, e para demonstrar princípios de engenharia de agentes relevantes para pesquisa/indústria: separação entre caminho barato/determinístico e caminho caro/inteligente, segurança contra prompt injection em conteúdo não confiável (e-mail), fallback entre provedores de LLM, e verificação/validação como parte central do design — não um detalhe.

### Fora de escopo (explícito)
- O sistema **nunca** executa ações financeiras reais (transferências, pagamentos, investimentos). É estritamente um sistema de observação, estruturação e análise.
- Integração via Open Finance/Open Banking Brasil fica fora do escopo inicial (exige credenciamento regulatório inviável para um projeto pessoal solo) — a arquitetura de ingestão foi desenhada para permitir essa evolução futura sem retrabalho, caso vire prioridade.

---

## 2. Arquitetura Geral

```
┌─────────────────────┐
│  GitHub Actions      │  (cron diário)
│  Serviço de Triagem   │──▶ Gmail API (escopo readonly)
└──────────┬───────────┘        │
           │ filtro regex/remetente (sem LLM)
           │ só segue adiante se houver match
           ▼
┌─────────────────────────────┐
│  Agente API (Render, free)   │
│  ┌─────────────────────────┐ │
│  │ Pipeline de Estruturação │ │  (fixo, sequencial)
│  │ Extração → Categorização │ │
│  │      → Validação         │ │
│  └───────────┬─────────────┘ │
│              │                │
│  ┌───────────▼─────────────┐ │
│  │  Persistência             │ │
│  └───────────┬─────────────┘ │
│              │                │
│  ┌───────────▼─────────────┐ │
│  │ Memória de Longo Prazo   │ │  (consolidação periódica)
│  │ (RAG sobre padrões)      │ │
│  └───────────┬─────────────┘ │
│              │                │
│  ┌───────────▼─────────────┐ │
│  │ Agente Conversacional    │ │  (orquestrador dinâmico)
│  │ (coach — chat + insights)│ │
│  └──────────────────────────┘ │
└──────────────┬────────────────┘
               │
     ┌─────────▼─────────┐
     │ MongoDB Atlas (M0)  │  dados estruturados
     │ Google Drive (15GB) │  documentos originais
     └─────────────────────┘
```

---

## 3. Componentes

### 3.1 Serviço de Triagem (Watcher)
- **Onde roda:** GitHub Actions, trigger agendado (`schedule`), execução diária.
- **O que faz:** consulta a API do Gmail (escopo `gmail.readonly`) filtrando por remetente conhecido (`@nubank.com.br`, expansível para outros bancos) e padrão de assunto via regex (ex: "fatura", "extrato").
- **Idempotência:** mantém registro dos IDs de mensagem já processados (coleção dedicada no MongoDB Atlas) para nunca reprocessar o mesmo e-mail.
- **Saída:** se houver match, faz uma chamada HTTP autenticada (token compartilhado) para o endpoint de ingestão do Agente API, enviando o conteúdo/anexo do e-mail.
- **Por que não usa LLM aqui:** filtro determinístico é ordens de magnitude mais barato e não expõe o LLM a conteúdo não filtrado — reduz tanto custo quanto superfície de prompt injection.

### 3.2 Pipeline de Estruturação (agentes fixos)
Sequência fixa e determinística — a maioria dos e-mails segue esse caminho sem intervenção do orquestrador dinâmico:

1. **Agente de Extração** — lê o PDF/corpo do e-mail e extrai transações brutas (data, estabelecimento, valor, parcela quando aplicável).
2. **Agente de Categorização** — classifica cada transação, usando RAG sobre categorizações anteriores do próprio usuário para manter consistência ao longo do tempo.
3. **Agente de Validação** — sinaliza duplicatas, valores fora do padrão histórico, ou dados malformados. Casos sinalizados aqui são o gatilho para escalar ao Agente Conversacional (ver 3.5).

### 3.3 Camada de Armazenamento
- **MongoDB Atlas (free tier M0, 512MB):** transações estruturadas, categorias, resumos mensais e periódicos (incluindo cortes incrementais, ex: quinzenal), histórico de chats, IDs de e-mail processados, metadados/ponteiros dos documentos, registro de bancos monitorados (ver 3.2.1) e embeddings de memória (ver 3.4).
  - Estimativa de volume: registros de transação e resumos são pequenos (centenas de bytes a poucos KB cada); mesmo com anos de histórico, o uso esperado fica bem abaixo dos 512MB. Avaliado e descartado o uso de um segundo provedor (ex: Supabase) para os dados estruturados — o free tier do Supabase tem capacidade similar (500MB) mas com a desvantagem de pausar automaticamente projetos após 7 dias de inatividade, exigindo despausar manualmente. O MongoDB Atlas free tier não expira nem pausa, e já suporta vetores nativamente (ver 3.4), então não há ganho real em dividir entre dois provedores.
- **Google Drive (15GB grátis):** armazenamento organizado dos documentos originais (PDF/e-mail), referenciados por metadado no MongoDB. Mantém o cluster do Mongo enxuto.

### 3.2.1 Registro de Bancos Monitorados (extensibilidade do Watcher)
- Coleção dedicada no MongoDB (`bank_sources`) com um documento por banco monitorado: `bank_id`, `sender_patterns` (remetentes/domínios), `subject_patterns` (regex de assunto), `active`.
- O Serviço de Triagem lê esse registro a cada execução e filtra contra todas as entradas ativas — adicionar um banco novo (ex: Itaú) é inserir um documento na coleção, não alterar código.
- Como o Agente de Extração usa LLM (não um parser rígido por banco), ele tende a lidar razoavelmente bem com o formato de um banco novo sem template dedicado; o Agente de Validação sinaliza casos em que a extração parecer inconsistente por causa de um layout desconhecido — podendo então, se necessário, receber um prompt/template específico para aquele banco.

### 3.4 Memória de Longo Prazo (RAG)
- Camada separada do dado transacional bruto: um índice de **padrões consolidados** (ex: "gasto médio em transporte", "tendência de aumento em assinaturas", metas declaradas pelo usuário).
- Atualizada por um processo de consolidação periódico (não a cada transação), para não virar ruído.
- É essa camada que dá "continuidade" ao coach — ele lembra de conversas e padrões passados sem precisar reprocessar todo o histórico bruto a cada pergunta.
- **Armazenamento dos embeddings:** MongoDB Atlas Vector Search, disponível também no tier gratuito M0 — os vetores ficam na mesma base que os demais dados, sem necessidade de um banco vetorial separado.
- **Modelo de embedding:** Gemini Embedding (`gemini-embedding-001`), disponível no tier gratuito da API do Gemini com cota própria (separada da cota de geração de texto). Volume esperado é baixo, já que a consolidação roda periodicamente, não por transação.

### 3.5 Agente Conversacional (orquestrador dinâmico)
- O único componente verdadeiramente "agentico" no sentido de decidir dinamicamente o que fazer — os demais seguem pipeline fixo.
- Ferramentas disponíveis: consulta ao MongoDB (dados estruturados), busca na memória RAG, acesso aos documentos originais no Drive.
- Acionado em dois contextos: (a) conversa direta com o usuário, (b) escalonamento vindo do Agente de Validação quando algo foge do padrão esperado.
- Gera também insights proativos (ex: resumo mensal) sem que o usuário precise perguntar.

### 3.6 Plataforma/Dashboard
- Interface web simples para visualizar gastos por categoria, tendências ao longo do tempo, navegar pelos documentos arquivados, e conversar com o coach.
- Não é o foco inicial do projeto — ver Roadmap (Seção 6).

---

## 4. Estratégia de LLM (orçamento zero)

| Papel | Provedor primário | Fallback |
|---|---|---|
| Agentes fixos (extração, categorização, validação) | Gemini API free tier (Flash/Flash-Lite) | OpenRouter free tier (Llama 3.3 70B / DeepSeek R1) |
| Agente Conversacional (coach) | Gemini API free tier | OpenRouter free tier |

**Por que esse arranjo:**
- Gemini free tier (2026): sem cartão, sem expiração, mas limites justos para uso agentico — verificar valores atuais na página oficial antes de implementar, pois mudaram várias vezes ao longo de 2026 (ordem de grandeza: ~15 RPM, algumas centenas a ~1.500 RPD, 1M TPM nos modelos Flash/Flash-Lite).
- **Trade-off de privacidade documentado conscientemente:** no tier gratuito, o Google pode usar prompts/respostas para melhorar seus modelos — dado financeiro (mesmo que só metadado extraído) passa por isso. Não há alternativa 100% local viável dado que o agente roda no Render (não no notebook do usuário) — decisão aceita conscientemente para este projeto de portfólio.
- **OpenRouter como fallback:** orçamento de rate limit totalmente separado (20 RPM, 50-1.000 RPD dependendo de compra prévia de créditos), modelos abertos (Llama, DeepSeek, Qwen — não inclui Gemini). Entra em ação quando o Gemini retorna 429, via lógica de fallback simples (API compatível com padrão OpenAI).

**Mitigações de engenharia necessárias (não opcionais):**
- Rate limiting / fila no Agente API — processa uma tarefa por vez respeitando o RPM disponível, com backoff exponencial em erro 429.
- Teto máximo de passos (tool-calls) por tarefa do Agente Conversacional, para evitar que um loop de raciocínio consuma o orçamento de requisições sozinho.
- Cuidado especial em cargas de backfill (importar anos de extrato de uma vez): processar em fila, não em paralelo.

---

## 5. Segurança e Confiabilidade

- **Least privilege no Gmail:** escopo `gmail.readonly`, idealmente restrito por filtro de rótulo/remetente quando possível.
- **E-mail como superfície de prompt injection:** conteúdo de e-mail (corpo, anexo) é tratado como **dado, nunca como instrução**, em todos os agentes do pipeline. Esse princípio deve ser documentado explicitamente no código/prompts do sistema, não só como boa intenção.
- **Autenticação interna:** a chamada do Serviço de Triagem (GitHub Actions) para o Agente API (Render) usa um token compartilhado — o endpoint não fica aberto publicamente sem autenticação.
- **Idempotência:** IDs de mensagem processados são rastreados para evitar duplicação de dados em reexecuções do cron.
- **Cold start do Render:** o serviço free do Render "dorme" após 15 minutos de inatividade e leva ~30-60s para acordar na próxima requisição — aceitável para um sistema de uso pessoal não crítico em tempo real (checagem diária, chat ocasional).

---

## 6. Roadmap de Construção Incremental

1. **Fase 1 — Ingestão + Estruturação:** Serviço de Triagem + pipeline fixo (extração, categorização, validação) + persistência no MongoDB/Drive. Já entrega valor sozinho: extratos organizados e categorizados automaticamente.
2. **Fase 2 — Memória + Coach:** camada de memória RAG consolidada + Agente Conversacional com acesso às ferramentas de consulta.
3. **Fase 3 — Dashboard:** interface web para visualização e chat.

Cada fase é testável e demonstrável isoladamente — boa estrutura também para o portfólio (cada fase pode virar um post/demo independente).

---

## 7. Riscos e Trade-offs Conhecidos

- **Parsing de PDF varia por banco:** cada banco tem layout de fatura/extrato diferente — o Agente de Extração precisa ser ajustado/testado especificamente para o formato do Nubank inicialmente, com extensão planejada (não implementada) para outros bancos.
- **Limites de rate limit do Gemini/OpenRouter mudam com frequência:** conferir valores atuais antes de dimensionar qualquer teste de carga ou backfill grande.
- **Free tier do Gemini usa dados para treinamento:** decisão consciente documentada na Seção 4 — não é um descuido.
- **MongoDB Atlas free tier tem 512MB:** suficiente para o volume esperado (transações + metadados, documentos ficam no Drive), mas vale monitorar conforme o histórico cresce ao longo dos anos.

---

## 8. Próximos Passos

- Definir nome do projeto e criar o repositório.
- Detalhar o schema de dados do MongoDB (transações, categorias, resumos, IDs processados).
- Levar este documento para a etapa de plano de implementação (quebra em tarefas concretas da Fase 1).

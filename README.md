# Meliuz - Analise de Teste A/B de Cashback

## O que esse projeto faz

Dado um CSV de um teste A/B de cashback (grupo de usuarios x data x compradores x comissao x cashback x vendas), o projeto:

1. Calcula KPIs de cada grupo (lucro liquido, ROI, lucro por comprador, GMV, compradores totais e mais 11 metricas complementares).
2. Aplica uma regra deterministica para eleger o grupo vencedor (priorizando maior lucro liquido, validado por ROI, eficiencia e escala).
3. Envia um JSON estruturado para a OpenAI, que retorna uma narrativa analitica explicando a decisao.
4. Gera graficos, um relatorio em PDF com identidade visual Meliuz e registra o resultado em uma planilha Google Sheets.

**Stack:** Python + pandas + matplotlib + reportlab + OpenAI API + Playwright (Google Sheets) + React (frontend web).

## Documentação técnica

- **`docs/RESUMO_DESENVOLVIMENTO.md`** — documentação completa do projeto: schema do CSV, banco de KPIs (decisão e complementares), regra de decisão com parâmetros e critérios, checklist de implementação.
- **`estudo/`** — notebooks Jupyter utilizados durante a fase de exploração e validação dos dados.

**Output esperado por parceiro analisado:**
- `outputs/<parceiro>/analise.json` — JSON auditavel com todos os KPIs, ranking, alertas e decisao.
- `outputs/<parceiro>/graficos/` — 5 PNGs (lucro, ROI vs lucro, composicao, rentabilidade, guardrails de escala).
- `outputs/<parceiro>/relatorio.md` — Relatorio em Markdown.
- `outputs/<parceiro>/relatorio.pdf` — Relatorio em PDF com identidade visual, graficos e rodape com assinatura + data.
- Planilha de sua escolha atualizada no GoogleSheets

## Como rodar (interface web)

## Pré-requisitos

- **Python** 3.11+ ([python.org](https://www.python.org/downloads/))
- **Node.js** 18+ ([nodejs.org](https://nodejs.org/))

## Passo a passo

```powershell
# 1. Instalar dependências Python
pip install -r requirements.txt

# 2. Instalar navegador para Google Sheets
python -m playwright install chromium

# 3. Instalar dependências do frontend
cd frontend
npm install
cd ..

# 4. Criar arquivo .env
@"
OPENAI_API_KEY=sk-sua_chave_openai
OPENAI_MODEL=gpt-5.4-mini
OPENAI_MAX_OUTPUT_TOKENS=5000
MELIUZ_SHEETS_URL=https://docs.google.com/spreadsheets/d/ID_DA_PLANILHA/edit?gid=0#gid=0
"@ | Out-File -FilePath .env -Encoding utf8
```

A planilha do Google Sheets precisa estar com permissão de **edição para qualquer pessoa com o link**.

```powershell
# 5. Rodar (sobe API + frontend juntos)
cd frontend
npm run dev
```

Acesse **http://localhost:3000**, clique ou arraste um CSV para iniciar a análise.

## Próximos passos

### 1. Melhorar frontend
A interface atual é funcional mas minimalista. Um redesign com componentes mais sofisticados, feedback visual durante o processamento (barra de progresso real, não apenas texto), tratamento de erros mais amigável e responsividade para mobile tornariam a experiência do usuário muito mais profissional.

### 2. Dockerizar o projeto
Empacotar a aplicação em containers Docker elimina a necessidade de instalar Python, Node.js e Playwright manualmente. Um `docker compose up` seria suficiente para subir tudo, garantindo consistência entre ambientes (desenvolvimento, staging, produção) e facilitando o deploy em qualquer cloud.

### 3. Chatbot no frontend
Implementar uma interface de chat onde o usuário possa "conversar com os dados":
- Fazer perguntas em linguagem natural sobre o CSV enviado (ex.: "qual grupo teve maior ROI?", "mostre a evolução diária do lucro").
- Solicitar análises específicas sem precisar reenviar o arquivo.
- Isso agregaria valor principalmente para times de negócio que não têm familiaridade com ferramentas analíticas tradicionais.

### 4. Mais KPIs e combos de KPIs
Expandir o banco de métricas com KPIs setoriais (ex.: CAC, LTV, margem por canal) e permitir que o usuário selecione combos de KPIs para análise, em vez de uma bateria fixa. Um sistema de "plano de análise" configurável por parceiro ou tipo de campanha traria flexibilidade para cenários variados.

### 5. Autenticação e multitenancy
Adicionar login (Google OAuth, Magic Link) para que diferentes times/parceiros acessem apenas suas próprias análises, com histórico persistido e dashboard consolidado.

### 6. CI/CD com testes automatizados
Pipeline de integração contínua rodando lint, type check e testes unitários no backend (pytest) e frontend (vitest) a cada push. Deploy automatizado via GitHub Actions para uma VPS ou serviço gerenciado (Railway, Fly.io).

### 7. Cache e fila de processamento
Análises longas (especialmente com LLM e Sheets) deveriam rodar em background com fila (Redis + Celery ou similar), permitindo que o usuário feche a página e volte depois para ver o resultado, além de evitar timeouts em CSVs grandes.

### 8. Monitoramento e observabilidade
Logs estruturados, métricas de uso (quantas análises, tempo médio, taxa de erro) e tracing (OpenTelemetry) para identificar gargalos. Um health check endpoint e dashboard (Grafana) dariam visibilidade do sistema em produção.

## Estrutura de saída

```
outputs/<parceiro>/
  analise.json        — KPIs e decisão
  graficos/           — PNGs dos gráficos
  relatorio.md        — Relatório em Markdown
  relatorio.pdf       — Relatório em PDF
```

---

Agradecimento especial ao time da **Méliuz** pela oportunidade de desenvolver este projeto. Obrigado pela confiança, pelo suporte e por tornar possível a entrega de uma ferramenta que une análise de dados, inteligência artificial e experiência do usuário em um só produto.

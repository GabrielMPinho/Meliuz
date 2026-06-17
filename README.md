# Meliuz - Analise de Teste A/B de Cashback

## O que esse projeto faz

Dado um CSV de um teste A/B de cashback (grupo de usuarios x data x compradores x comissao x cashback x vendas), o projeto:

1. Calcula KPIs de cada grupo (lucro liquido, ROI, lucro por comprador, GMV, compradores totais e mais 11 metricas complementares).
2. Aplica uma regra deterministica para eleger o grupo vencedor (priorizando maior lucro liquido, validado por ROI, eficiencia e escala).
3. Envia um JSON estruturado para a OpenAI, que retorna uma narrativa analitica explicando a decisao.
4. Gera graficos, um relatorio em PDF com identidade visual Meliuz e registra o resultado em uma planilha Google Sheets.

**Stack:** Python + pandas + matplotlib + reportlab + OpenAI API + Playwright (Google Sheets).

**Output esperado por parceiro analisado:**
- `outputs/<parceiro>/analise.json` — JSON auditavel com todos os KPIs, ranking, alertas e decisao.
- `outputs/<parceiro>/graficos/` — 5 PNGs (lucro, ROI vs lucro, composicao, rentabilidade, guardrails de escala).
- `outputs/<parceiro>/relatorio.md` — Relatorio em Markdown.
- `outputs/<parceiro>/relatorio.pdf` — Relatorio em PDF com identidade visual, graficos e rodape com assinatura + data.
- Planilha de sua escolha atualizada no GoogleSheets

## Como rodar (passo a passo para qualquer maquina)

### 1. Instalar Python

Baixe o instalador em https://www.python.org/downloads/ (versao 3.11 ou superior).
Durante a instalacao, marque **"Add Python to PATH"** e clique em Instalar.

Para confirmar, abra o terminal (PowerShell) e digite:

```powershell
python --version
```

### 2. Baixar o projeto

Fac¸a o download dos arquivos ou clone o repositorio.

Entre na pasta do projeto:

```powershell
cd caminho\para\Meliuz
```

### 3. Configurar arquivos

**3.1. Arquivo `.env`**

Crie o arquivo `.env` na raiz do projeto com o seguinte conteudo:

```env
OPENAI_API_KEY=sk-sua_chave_real_da_openai_aqui
OPENAI_MODEL=gpt-5.4-mini
OPENAI_MAX_OUTPUT_TOKENS=5000
MELIUZ_SHEETS_URL=https://docs.google.com/spreadsheets/d/ID_DA_SUA_PLANILHA/edit?gid=0#gid=0
```

- `OPENAI_API_KEY`: sua chave da OpenAI (crie em https://platform.openai.com/api-keys).
- `OPENAI_MODEL`: modelo da OpenAI (`gpt-5.4-mini` e o mais barato; `gpt-5.5` e o recomendado para producao).
- `MELIUZ_SHEETS_URL`: URL da planilha Google Sheets que recebera o tracking. A planilha precisa estar **publica** e com permissao de **edicao para qualquer pessoa com o link**.


**3.2. Dados de entrada**

Coloque os CSVs dos testes A/B dentro da pasta `data/`. O projeto ja vem com 3 datasets de exemplo:

- `data/dataset_01_parceiroA.csv`
- `data/dataset_02_parceiroB.csv`
- `data/dataset_03_parceiroC.csv`

### 4. Instalar dependencias

No terminal (dentro da pasta do projeto):

```powershell
pip install -r requirements.txt
```

### 5. Instalar navegador para Google Sheets

O projeto usa Playwright para atualizar a planilha automaticamente. Execute:

```powershell
python -m playwright install chromium
```

Isso baixa uma copia do Chromium para uso exclusivo do script.

### 6. Rodar a analise

**Modo basico (gera JSON, graficos, relatorio Markdown e PDF, sem planilha):**

```powershell
python src\pipeline.py data\dataset_01_parceiroA.csv --llm openai
```

**Modo completo (tudo acima + atualiza a planilha Google Sheets):**

```powershell
python src\pipeline.py data\dataset_01_parceiroA.csv --llm openai --update-sheets
```

Cada execucao adiciona uma nova linha na planilha sem apagar as anteriores (append).

### 7. Ver os resultados

Apos rodar, os arquivos estarao em:

```
outputs/
  parceiro_a/
    analise.json
    graficos/*.png
    relatorio.md
    relatorio.pdf
  parceiro_b/
    ...
  parceiro_c/
    ...
```

## Sobre o RESUMO_DESENVOLVIMENTO.md

O arquivo `docs/RESUMO_DESENVOLVIMENTO.md` e a documentacao tecnica completa do projeto. Ele contem:

- **Pergunta central** que o projeto responde.
- **Input esperado:** schema do CSV.
- **Output esperado:** JSON, graficos, relatorio PDF e tracking no Sheets.
- **Stack pensada:** fluxo completo (ETL -> KPIs -> decisao -> LLM -> PDF -> Sheets).
- **Banco de KPIs:** descricao de cada KPI de decisao (5) e complementar (11), com formulas e ordem de prioridade.
- **Regra de decisao:** parametros, elegibilidade, criterios de escala, logica de vencedor, empate tecnico, desempate e alertas.
- **Checklist de implementacao:** tudo que foi feito e o que ainda pode ser evoluido.

Leia-o se quiser entender em detalhes como a decisao e calculada e quais criterios sao usados.

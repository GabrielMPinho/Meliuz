# Implementacao

## O que fazer para implementar

### 1. Configurar variaveis de ambiente

Copie o `.env.example` para `.env` e preencha os valores locais:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-5.4-mini
OPENAI_MAX_OUTPUT_TOKENS=5000
MELIUZ_SHEETS_URL=https://docs.google.com/spreadsheets/d/SEU_ID_DA_PLANILHA/edit?gid=0#gid=0
```

O `.env` esta no `.gitignore` para evitar publicar chaves e configuracoes
locais por acidente. O `.env.example` deve ser commitado como template seguro.

Para o tracking funcionar, a planilha definida em `MELIUZ_SHEETS_URL` precisa
estar publica e permitir alteracoes para qualquer pessoa com o link.

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Rodar com LLM real

Para testar com custo menor:

```powershell
python src\pipeline.py data\dataset_01_parceiroA.csv --llm openai
```

O pipeline vai:

1. limpar o CSV;
2. calcular KPIs;
3. gerar o JSON auditavel;
4. gerar graficos;
5. enviar o JSON auditavel para a OpenAI;
6. receber um JSON com `blocos_escolhidos` e `narrativa_markdown`;
7. validar a resposta com `validacao_llm.py`;
8. montar `outputs/<parceiro>/relatorio.md`;
9. montar `outputs/<parceiro>/relatorio.pdf`.

Para gerar o PDF e atualizar a planilha de tracking ao final da analise:

```powershell
python src\pipeline.py data\dataset_01_parceiroA.csv --llm openai --update-sheets
```

A planilha recebe uma linha por teste analisado, com as colunas minimas do
tracking e os ganhadores de cada KPI de decisao. A atualizacao e feita por
append: cada nova analise entra na proxima linha vazia, sem apagar resultados
anteriores.

- nome do teste;
- teste realizado em;
- parceiro;
- periodo;
- descricao;
- vencedor;
- resultado;
- decisao tomada;
- grupo e valor do maior `lucro_liquido`;
- grupo e valor do maior `roi`;
- grupo e valor do maior `lucro_por_comprador`;
- grupo e valor do maior `gmv`;
- grupo e valor do maior `total_compradores`.

Tambem existe um script isolado para atualizar apenas a planilha com um ou mais
CSVs, sem gerar PDF:

```powershell
python src\atualizar_sheets.py data\dataset_01_parceiroA.csv data\dataset_02_parceiroB.csv data\dataset_03_parceiroC.csv
```

Esse script tambem faz append. Se quiser reconstruir a planilha do zero, limpe
a aba manualmente antes de rodar.

Para apenas migrar o cabecalho da planilha para o schema atual, sem adicionar
uma nova linha:

```powershell
python src\atualizar_sheets.py --migrate-schema
```

Para trocar a planilha, altere `MELIUZ_SHEETS_URL` no `.env` ou passe
`--sheet-url`.

Como a planilha precisa estar publica com permissao de edicao, a atualizacao
usa Chrome ou Edge via Playwright para colar as novas linhas na proxima linha
vazia. Se o navegador nao for encontrado automaticamente, defina
`MELIUZ_CHROME_PATH` no `.env`.

O PDF usa identidade visual inspirada na Meliuz, com rosa como cor principal,
cabecalho de marca, graficos, tabelas e rodape em todas as paginas com:

```text
Gabriel Manata de Pinho · Analise em DD/MM/AAAA · Pagina N
```

### 4. Modelo de teste

Para teste local, o projeto usa `gpt-5.4-mini` em `OPENAI_MODEL`.

Motivo: e um modelo mais barato e rapido que a familia principal, mas ainda e
mais adequado que um modelo `nano` para uma narrativa analitica com regras,
comparacoes e formato JSON validavel. Modelos `nano` devem ficar para tarefas
muito estreitas, com saidas curtas e fechadas.

### 5. Modelo recomendado para producao

Para producao, usar `gpt-5.5`.

Motivo: a documentacao atual da OpenAI posiciona GPT-5.5 como o ponto de partida
para a maioria dos workloads de raciocinio, com melhor execucao de tarefas,
melhor uso de instrucoes e boa adequacao para fluxos de producao mais complexos.
Neste projeto, a LLM nao calcula a decisao, mas precisa produzir uma narrativa
executiva consistente, seguir restricoes, respeitar o vencedor calculado e
retornar JSON valido. Isso favorece um modelo mais robusto em producao.

Se o custo for uma restricao forte, mantenha `gpt-5.4-mini` em producao somente
depois de comparar validacao, qualidade da narrativa e taxa de retrabalho em uma
amostra dos relatorios.

Referencias oficiais:

- Responses API: https://platform.openai.com/docs/api-reference/responses
- Structured Outputs: https://developers.openai.com/api/docs/guides/structured-outputs
- Modelo mais recente: https://developers.openai.com/api/docs/guides/latest-model
- Reasoning models: https://developers.openai.com/api/docs/guides/reasoning

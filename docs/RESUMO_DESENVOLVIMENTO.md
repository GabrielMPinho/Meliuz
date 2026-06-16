# Escopo do Case - Teste A/B de Cashback

## 1. Pergunta Central

> "Dado esse teste A/B, qual variante de cashback devemos escalar pra 100% do trafego?"

**Traduzindo:** dado o parceiro do CSV, qual grupo de usuario possui as melhores metricas? Implementar a politica deles para os outros grupos.


## 2. Input

CSV padronizado com o seguinte schema:

| Coluna | Tipo | Descricao |
|---|---|---|
| Data | YYYY-MM-DD | Data da observacao |
| Grupos de usuarios | string | Variante do teste (Grupo 1, Grupo 2, Grupo 3) |
| Parceiro | string | Parceiro do teste (A, B ou C) |
| compradores | int | Usuarios unicos que compraram no dia |
| comissao | string (R$) | Comissao paga pelo parceiro ao Meliuz no dia |
| cashback | string (R$) | Cashback distribuido aos usuarios no dia |
| vendas totais | string (R$) | GMV (valor total das vendas) no dia |



## 3. Output

1. **Relatorio dos testes A/B:** PDF carregado com a analise completa: graficos, tabelas e decisao final.
2. **Resumo registrado em uma planilha Google Sheets.**
   - Colunas minimas: nome do teste, descricao, resultado e decisao tomada.

## 4. Stack Pensada

1. Usuário descreve o teste + envia CSV
2. Python faz ETL
3. Python calcula todos os KPIs
4. Python aplica regra de decisão e define vencedor
5. Python monta um catálogo de KPIs e combos permitidos
6. LLM escolhe quais blocos explicativos destacar de acordo com o prompt do usuário
7. Python valida a escolha da LLM
8. LLM escreve narrativa usando apenas os blocos aprovados
9. Python monta PDF + registra CSV/Sheets

## 5. KPIs para Analise

**O que deve ser respondido:** dado o parceiro do CSV, qual grupo de usuario possui as melhores metricas? Implementar a politica deles para os outros grupos.

### 5.1. Banco de KPIs para Definir Vencedor

| Ordem | Escopo | KPI | Descricao |
|---:|---|---|---|
| 1 | KPI primario | **Lucro líquido total** | Qual grupo esta gerando o maior lucro? (Comissao - cashback). Bom indicador de sucesso. |
| 2 | KPI de eficiencia | **ROI** | Qual grupo esta sendo o mais efetivo? Pra cada R$ 1 investido, eu tive X de lucro. (Lucro / cashback). |
| 3 | KPI de eficiencia | **Lucro por comprador** | Quanto, em media, cada comprador gerou de lucro. (Lucro / compradores). |
| 4 | KPI de volume | **GMV** | Qual grupo vendeu mais? Nao adianta ter um lucro maior se perdeu no volume. (Soma das vendas). |
| 5 | KPI de volume | **Compradores totais** | Qual grupo tem mais compradores? O lucro não deve existir a custa do volume de vendas. (Soma dos compradores). |

O vencedor sera aquele que tiver o maior lucro liquido total, com um bom retorno sobre o investimento e com um bom lucro por comprador, sem perder em escala.

#### 5.1.1. Combos de KPIs para Explicar Vitoria ou Derrota

| Ordem | Combo | Pergunta que responde | Como ajuda na decisao |
|---:|---|---|---|
| 1 | **Lucro líquido total + ROI + Lucro por comprador + GMV** | O grupo combina impacto financeiro, eficiencia, rentabilidade unitaria e escala? | Resume os principais criterios de decisao e ajuda a justificar por que o grupo e o melhor candidato para escalar. |
| 2 | **Lucro líquido total + GMV + Compradores totais** | O lucro veio mantendo volume relevante? | Mostra se o grupo gerou lucro sem perder escala de vendas e compradores. |
| 3 | **ROI + Cashback total + Cashback sobre GMV** | O cashback investido foi eficiente ou caro demais? | Ajuda a entender se o retorno veio de uma politica saudavel de incentivo ou de um gasto excessivo com cashback. |
| 4 | **Lucro por comprador + Comissao por comprador + Cashback por comprador** | Cada comprador gera valor suficiente depois do incentivo? | Explica a rentabilidade unitaria: quanto cada comprador gera de receita, quanto custa em cashback e quanto sobra de lucro. |
| 5 | **GMV + Compradores totais + Ticket medio** | O volume veio de muitos compradores ou de compras maiores? | Ajuda a interpretar a escala do grupo e identificar se o resultado dependeu mais de alcance ou de ticket. |

### 5.2. Banco de KPIs Complementares para Analise Geral

A ideia deste banco nao e repetir os KPIs de decisao. Os KPIs abaixo ajudam a
explicar o contexto do resultado, mas nao definem o vencedor sozinhos. O Python
calcula todos, e a LLM escolhe quais blocos complementares fazem sentido para
explicar o teste.

| Ordem | Escopo | KPI | Descricao |
|---:|---|---|---|
| 1 | KPI de receita | **Comissao total** | Quanto o Meliuz recebeu do parceiro. (Soma da comissao). |
| 2 | KPI de custo | **Cashback total** | Quanto foi gasto para incentivar os usuarios. (Soma do cashback). |
| 3 | KPI de ticket | **Ticket medio** | Quanto cada comprador gastou, em media. (GMV / compradores). |
| 4 | KPI de eficiencia | **Comissao por comprador** | Quanto de receita cada comprador gerou para o Meliuz. (Comissao / compradores). |
| 5 | KPI de custo unitario | **Cashback por comprador** | Quanto custou, em media, incentivar cada comprador. (Cashback / compradores). |
| 6 | KPI de margem | **Margem liquida sobre GMV** | Quanto do volume vendido virou lucro liquido para o Meliuz. (Lucro / GMV). |
| 7 | KPI de incentivo | **Cashback sobre GMV** | Quao agressiva foi a politica de cashback. (Cashback / GMV). |
| 8 | Sinal de confianca | **Gap de lucro vs 2o colocado** | Diferenca percentual de lucro entre o vencedor e o segundo colocado. Ajuda a separar vitoria clara de decisao apertada. |
| 9 | Guardrail de escala | **Perda de GMV vs maior GMV** | Quanto o grupo perdeu de GMV em relacao ao grupo com maior volume. |
| 10 | Guardrail de escala | **Perda de compradores vs maior compradores** | Quanto o grupo perdeu de compradores em relacao ao grupo com mais compradores reportados. |
| 11 | Sinal de estabilidade | **Dias com lucro negativo** | Quantidade ou percentual de dias em que o grupo teve lucro liquido negativo. Ajuda a identificar resultado instavel. |
| 12 | Qualidade de dados | **Alertas de denominador zero** | Indica casos em que cashback, compradores ou GMV sao zero e alguma metrica precisa ser tratada com cuidado. |

#### 5.2.1. Combos de KPIs para Contar a Historia

| Ordem | Combo | Pergunta que responde | Leitura analitica |
|---:|---|---|---|
| 1 | **Comissao por comprador + Cashback por comprador + Lucro por comprador** | Cada comprador gera valor suficiente depois do incentivo? | Mostra a composicao da rentabilidade unitaria: quanto o comprador gera de receita, quanto custa em cashback e quanto sobra de lucro. |
| 2 | **GMV + Compradores totais + Ticket medio** | O volume veio de muitos compradores ou de compras maiores? | Explica a origem do volume de vendas: crescimento por escala de compradores ou por aumento do valor medio comprado. |
| 3 | **GMV + Margem liquida sobre GMV + Lucro liquido total** | O grupo vende muito e transforma esse volume em lucro? | Diferencia grupos que apenas movimentam muito dinheiro daqueles que realmente convertem o volume em lucro para o Meliuz. |
| 4 | **Cashback total + Cashback sobre GMV + ROI** | O incentivo foi caro demais ou eficiente? | Mostra se o grupo precisou gastar muito cashback para gerar resultado ou se o investimento trouxe retorno saudavel. |
| 5 | **Lucro liquido total + ROI + GMV** | O resultado combina impacto financeiro, eficiencia e escala? | Ajuda a comparar grupos que podem ter trade-offs diferentes: maior lucro, melhor eficiencia ou maior volume. |


## 6. Regra de Decisao

A decisao final deve ser calculada em Python. A LLM nao escolhe vencedor.

### 6.1. Parametros Configuraveis

Os thresholds abaixo sao defaults do case. Em um produto real, deveriam ser
calibrados com historico de testes e metas internas do negocio.

```python
LUCRO_TOLERANCE = 0.10
ROI_ADVANTAGE = 0.20
EMPATE_LUCRO = 0.05
EMPATE_ROI = 0.10
SCALE_OK_LIMIT = 0.20
SCALE_CRITICAL_LIMIT = 0.40
```

Interpretacao:

- `LUCRO_TOLERANCE`: o candidato de eficiencia pode perder ate 10% de lucro vs o candidato de lucro.
- `ROI_ADVANTAGE`: o candidato de eficiencia precisa ter ROI pelo menos 20% maior.
- `EMPATE_LUCRO`: gap de lucro abaixo de 5% entra como possivel empate tecnico.
- `EMPATE_ROI`: gap de ROI abaixo de 10% entra como possivel empate tecnico.
- `SCALE_OK_LIMIT`: perda de escala ate 20% e considerada ok.
- `SCALE_CRITICAL_LIMIT`: perda de escala acima de 40% torna o grupo inelegivel.

### 6.2. Elegibilidade

Um grupo so pode vencer se cumprir os criterios financeiros minimos:

- lucro liquido total > 0;
- ROI > 0;
- lucro por comprador > 0.

### 6.3. Escala (GMV + Compradores totais)

A escala deve ser avaliada contra o maior valor observado no proprio teste, não
necessariamente contra um grupo controle.

Calcular separadamente:

- perda de GMV vs maior GMV observado;
- perda de compradores vs maior compradores observado.

Classificacao:

- perda <= 20%: ok;
- 20% < perda <= 40%: alerta de escala, mas o grupo continua elegivel;
- perda > 40%: grupo inelegivel.

### 6.4. Caso sem Grupo Elegivel

Se nenhum grupo for elegivel, a recomendacao deve ser:

> Nao escalar. Revisar politica de cashback.

### 6.5. Caso com Apenas um Grupo Elegivel

Se apenas um grupo for elegivel, ele vence por `unico_elegivel`, nao por
`consenso`.

Esse caso deve ser sinalizado no relatorio, porque significa que os demais grupos
foram eliminados pelos criterios de elegibilidade.

### 6.6. Escolha do Vencedor

Entre os grupos elegiveis, a decisao considera dois candidatos:

- **Candidato de lucro**: grupo elegivel com maior lucro liquido total.
- **Candidato de eficiencia**: grupo elegivel com maior ROI.

Regra:

1. Se o candidato de lucro e o candidato de eficiencia forem o mesmo grupo, ele vence por consenso.
2. Se forem grupos diferentes, o candidato de eficiencia vence se:
   - lucro do candidato de eficiencia >= lucro do candidato de lucro * (1 - `LUCRO_TOLERANCE`);
   - ROI do candidato de eficiencia >= ROI do candidato de lucro * (1 + `ROI_ADVANTAGE`).
3. Empate tecnico:
   - `gap_lucro` < `EMPATE_LUCRO`;
   - `gap_roi` < `EMPATE_ROI`.
4. Se houver empate tecnico, a solucao deve mostrar o alerta:
   > Diferenca pequena demais entre grupo X e grupo Y para sustentar recomendacao forte com dados agregados.
5. Mesmo com empate tecnico, a solucao ainda deve definir um vencedor por desempate.
6. Caso contrario, vence o candidato de lucro.

Na pratica:

- o candidato de eficiencia pode vencer se tiver pelo menos 90% do lucro do candidato de lucro e 120% do ROI do candidato de lucro;
- se a diferenca dos lucros for menor que 5% do maior lucro entre os candidatos e a diferenca de ROI for menor que 10% do maior ROI entre os candidatos, existe empate tecnico;
- empate tecnico nao impede a decisao, apenas reduz a confianca da recomendacao;
- se nenhuma dessas condicoes acontecer, vence o candidato de lucro.

### 6.7. Como Calcular os Gaps

Usar os candidatos de lucro e eficiencia como referencia:

```text
gap_lucro = abs(lucro_A - lucro_B) / max(lucro_A, lucro_B)
gap_roi = abs(ROI_A - ROI_B) / max(ROI_A, ROI_B)
```

Onde:

- `A` = candidato de lucro;
- `B` = candidato de eficiencia.

### 6.8. Desempate

Se houver empate técnico entre Grupo X e Grupo Y:

1. Mostrar o alerta:
   > Diferenca pequena demais entre Grupo X e Grupo Y para sustentar recomendacao forte com dados agregados.
2. Desempatar por:
   - maior lucro por comprador;
   - maior GMV;
   - maior compradores totais.
3. Se ainda empatar em tudo, vence o candidato de lucro.

### 6.9. Alertas

- **Empate tecnico**: gap de lucro < 5% e gap de ROI < 10%.
- **Risco de escala**: perda de GMV ou compradores entre 20% e 40%.
- **Troca por eficiencia**: candidato de ROI venceu mesmo sem ter o maior lucro.
- **Risco de eficiencia**: candidato de lucro venceu, mas seu ROI ficou muito abaixo do melhor ROI do teste.
- **Unico elegivel**: apenas um grupo passou nos criterios de elegibilidade.

Para a V1, o empate tecnico usa apenas gap percentual. Uma evolucao futura pode
combinar esse criterio com um gap absoluto minimo em R$.


## 7. Checklist de Implementacao do Projeto

Objetivo: ao final deste checklist, a solucao deve ler os 3 datasets, calcular a decisao em Python, gerar narrativa com LLM, produzir relatorio e registrar o resultado final.

### 7.1. Base do Projeto

- [X] **Organizar estrutura minima do projeto**
  Manter `data/`, `docs/`, `src/`, `prompts/` e `outputs/`, separando dados de entrada, documentacao, codigo, prompts e arquivos gerados.

- [x] **Fazer ETL inicial**
  Criar uma funcao que leia qualquer CSV do case, normalize nomes de colunas, trate datas, limpe campos monetarios, padronize textos e retorne um dataframe pronto para calculo.

### 7.2. Calculos em Python

- [x] **Calcular KPIs de decisao**
  Implementar os KPIs obrigatorios usados na escolha do vencedor.

  - [x] **Lucro liquido total**: comissao total - cashback total.
  - [x] **ROI**: lucro liquido total / cashback total.
  - [x] **Lucro por comprador**: lucro liquido total / compradores totais.
  - [x] **GMV**: soma de vendas totais.
  - [x] **Compradores totais**: soma de compradores.

- [x] **Calcular KPIs complementares**
  Implementar os 11 KPIs extras do banco de analise geral, sem repetir os KPIs principais de decisao.

  - [x] **Comissao total**: soma de comissao.
  - [x] **Cashback total**: soma de cashback.
  - [x] **Ticket medio**: GMV / compradores totais.
  - [x] **Comissao por comprador**: comissao total / compradores totais.
  - [x] **Cashback por comprador**: cashback total / compradores totais.
  - [x] **Margem liquida sobre GMV**: lucro liquido total / GMV.
  - [x] **Cashback sobre GMV**: cashback total / GMV.
  - [x] **Gap de lucro vs 2o colocado**: diferenca percentual de lucro entre o vencedor e o segundo colocado.
  - [x] **Perda de GMV vs maior GMV**: diferenca percentual entre o grupo analisado e o grupo com maior GMV.
  - [x] **Perda de compradores vs maior compradores**: diferenca percentual entre o grupo analisado e o grupo com mais compradores.
  - [x] **Dias com lucro negativo**: quantidade ou percentual de dias em que o lucro liquido foi menor que zero.
  

### 7.3. Decisao e Auditoria

- [x] **Criar catalogo de KPIs e combos permitidos**
  Montar uma estrutura que informe para a LLM quais KPIs e combos existem, o que cada um explica e quando podem ser usados na narrativa.

- [x] **Implementar regra deterministica de decisao**
  Escolher o vencedor em Python, priorizando maior lucro liquido total e usando ROI, lucro por comprador, GMV e compradores como criterios de eficiencia, rentabilidade e escala.

- [x] **Definir tratamento para casos inconclusivos**
  Criar regra para quando nenhum grupo deve ser escalado, por exemplo quando todos falham em lucro, ROI, rentabilidade ou escala minima.

- [x] **Gerar JSON auditavel da analise**
  Criar um JSON com metadados do teste, KPIs por grupo, decisao calculada, ranking, guardrails, alertas e catalogo de blocos que a LLM pode usar.

### 7.4. LLM e Relatorio

- [x] **Criar prompt da LLM**
  Escrever prompts em `prompts/` deixando claro que a LLM nao calcula KPIs, nao troca o vencedor e apenas escolhe os blocos explicativos mais relevantes.

- [x] **Validar escolha da LLM**
  Conferir em Python se os KPIs e combos escolhidos pela LLM existem no catalogo permitido e se a narrativa respeita a decisao calculada.

- [x] **Gerar graficos principais**
  Criar graficos objetivos para lucro liquido, ROI vs lucro, composicao comissao/cashback, rentabilidade por comprador e guardrails de escala.

- [ ] **Montar relatorio final**
  Gerar um relatorio apresentavel com sumario executivo, decisao, justificativa, tabela de KPIs, graficos, riscos, limitacoes e proximo passo recomendado.

### 7.5. Entrega

- [ ] **Registrar resultado em tracking**
  Salvar uma linha por teste analisado em Google Sheets, contendo nome do teste, parceiro, periodo, vencedor, resultado e decisao tomada.

- [ ] **Rodar a solucao nos 3 datasets**
  Executar a mesma logica para Parceiro A, Parceiro B e Parceiro C sem alterar codigo entre os arquivos.

- [ ] **Revisar outputs finais**
  Conferir se cada parceiro possui JSON, graficos, relatorio e linha no tracking, e se a recomendacao esta coerente com a regra definida.

- [ ] **Criar README do projeto**
  Explicar objetivo, arquitetura, como rodar, entradas esperadas, outputs gerados, regra de decisao, uso da LLM e limitacoes da analise.

- [ ] **Preparar entrega no GitHub**
  Garantir que o repositorio esta limpo, publico, sem credenciais, com dados, codigo, README, relatorios gerados e tracking final.

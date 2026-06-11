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

1. Frontend simples para envio do CSV
2. Script em Python para ETL + gráficos
3. Python calcula os KPIs e determina o vencedor por regra explícita.
4. LLM recebe os KPIs, os gráficos/tabelas resumidos, a decisão calculada e gera um relatorio executivo claro.
5. Script em Python recebe output e monta o PDF completo com a narrativa da LLM
6. Frontend mostra arquivos pronto para serem baixados e email é disparado 

## 5. KPIs para Analise

**O que deve ser respondido:** dado o parceiro do CSV, qual grupo de usuario possui as melhores metricas? Implementar a politica deles para os outros grupos.

### 5.1. KPIs para Definir Vencedor

| Ordem | Escopo | KPI | Descricao |
|---:|---|---|---|
| 1 | KPI primario | **Lucro total** | Qual grupo esta gerando o maior lucro? (Comissao - cashback). Bom indicador de sucesso. |
| 2 | KPI de eficiencia | **ROI** | Qual grupo esta sendo o mais efetivo? Pra cada R$ 1 investido, eu tive X de lucro. (Lucro / cashback). |
| 3 | KPI de eficiencia | **Lucro por comprador** | Quanto, em media, cada comprador gerou de lucro. (Lucro / compradores). |
| 4 | KPI de volume | **GMV** | Qual grupo vendeu mais? Nao adianta ter um lucro maior se perdeu no volume. (Soma das vendas). |

O vencedor sera aquele que tiver o maior lucro liquido total, com um bom retorno sobre o investimento e com um bom lucro por comprador, sem perder em escala.

#### 5.1.1. Combos de KPIs para Explicar Vitoria ou Derrota

| Ordem | Combo | Pergunta que responde | Como ajuda na decisao |
|---:|---|---|---|
| 1 | **Lucro total + ROI + Lucro por comprador + GMV** | O grupo combina impacto financeiro, eficiencia, rentabilidade unitaria e escala? | Resume os principais criterios de decisao e ajuda a justificar por que o grupo e o melhor candidato para escalar. |
| 2 | **Lucro total + GMV + Compradores totais** | O lucro veio mantendo volume relevante? | Mostra se o grupo gerou lucro sem perder escala de vendas e compradores. |
| 3 | **ROI + Cashback total + Cashback sobre GMV** | O cashback investido foi eficiente ou caro demais? | Ajuda a entender se o retorno veio de uma politica saudavel de incentivo ou de um gasto excessivo com cashback. |
| 4 | **Lucro por comprador + Comissao por comprador + Cashback por comprador** | Cada comprador gera valor suficiente depois do incentivo? | Explica a rentabilidade unitaria: quanto cada comprador gera de receita, quanto custa em cashback e quanto sobra de lucro. |
| 5 | **GMV + Compradores totais + Ticket medio** | O volume veio de muitos compradores ou de compras maiores? | Ajuda a interpretar a escala do grupo e identificar se o resultado dependeu mais de alcance ou de ticket. |

### 5.2. KPIs para Analise Geral

| Ordem | Escopo | KPI | Descricao |
|---:|---|---|---|
| 1 | KPI de receita | **Comissao total** | Quanto o Meliuz recebeu do parceiro. (Soma da comissao). |
| 2 | KPI de custo | **Cashback total** | Quanto foi gasto para incentivar os usuarios. (Soma do cashback). |
| 3 | KPI de volume | **Compradores totais** | Quantos usuarios unicos compraram no grupo. (Soma dos compradores). |
| 4 | KPI de ticket | **Ticket medio** | Quanto cada comprador gastou por grupo e geral, em media. (GMV / compradores). |
| 5 | KPI de eficiencia | **Comissao por comprador** | Quanto de receita cada comprador gerou para o Meliuz. (Comissao / compradores). |
| 6 | KPI de custo unitario | **Cashback por comprador** | Quanto custou, em media, incentivar cada comprador. (Cashback / compradores). |
| 7 | KPI de margem | **Margem liquida sobre GMV** | Quanto do volume vendido virou lucro liquido para o Meliuz. (Lucro / GMV). |
| 8 | KPI de incentivo | **Cashback sobre GMV** | Quão agressiva foi a politica de cashback. (Cashback / GMV). |

#### 5.2.1. Combos de KPIs para Contar a Historia

| Ordem | Combo | Pergunta que responde | Leitura analitica |
|---:|---|---|---|
| 1 | **Comissao por comprador + Cashback por comprador + Lucro por comprador** | Cada comprador gera valor suficiente depois do incentivo? | Mostra a composicao da rentabilidade unitaria: quanto o comprador gera de receita, quanto custa em cashback e quanto sobra de lucro. |
| 2 | **GMV + Compradores totais + Ticket medio** | O volume veio de muitos compradores ou de compras maiores? | Explica a origem do volume de vendas: crescimento por escala de compradores ou por aumento do valor medio comprado. |
| 3 | **GMV + Margem liquida sobre GMV + Lucro total** | O grupo vende muito e transforma esse volume em lucro? | Diferencia grupos que apenas movimentam muito dinheiro daqueles que realmente convertem o volume em lucro para o Meliuz. |
| 4 | **Cashback total + Cashback sobre GMV + ROI** | O incentivo foi caro demais ou eficiente? | Mostra se o grupo precisou gastar muito cashback para gerar resultado ou se o investimento trouxe retorno saudavel. |
| 5 | **Lucro total + ROI + GMV** | O resultado combina impacto financeiro, eficiencia e escala? | Ajuda a comparar grupos que podem ter trade-offs diferentes: maior lucro, melhor eficiencia ou maior volume. |

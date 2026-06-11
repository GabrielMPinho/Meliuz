## Pergunta central

> "Dado esse teste A/B, qual variante de cashback devemos escalar pra 100% do tráfego?"

**Traduzindo:** Dado o parceiro do csv, qual Grupo de usuário possui as melhores métricas? Implementar a política deles para os outros grupos.

---

## Input

CSV padronizado com o seguinte schema:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| Data | YYYY-MM-DD | Data da observação |
| Grupos de usuários | string | Variante do teste (Grupo 1, Grupo 2, Grupo 3) |
| Parceiro | string | Parceiro do teste (A, B ou C) |
| compradores | int | Usuários únicos que compraram no dia |
| comissão | string (R$) | Comissão paga pelo parceiro ao Méliuz no dia |
| cashback | string (R$) | Cashback distribuído aos usuários no dia |
| vendas totais | string (R$) | GMV (valor total das vendas) no dia |

## Output

1. **Relatório dos testes A/B:** Word (ou powerpoint?) carregado com a análise completa (gráficos, tabelas e decisão final)
2. **Resumo** registrado em uma planilha Google Sheets.
    - Colunas mínimas: nome do teste, descrição, resultado e decisão tomada.

---

## Stack Pensada

1. Script em python fazendo ETL completo.
2. Frontend simples e profissional para carregamento de dados.
3. Output enviado por email + disponibilizado no front.

---

## Análise

**O que deve ser respondido:** Dado o parceiro do csv, qual Grupo de usuário possui as melhores métricas? Implementar a política deles para os outros grupos.

### KPIs para definir vencedor

| # | KPI | Descrição |
|---|-----|-----------|
| 1 | **Lucro total** | Qual grupo está gerando o maior Lucro? (Comissão - cashback). Bom indicador de sucesso. |
| 2 | **ROI** | Qual grupo está sendo o mais efetivo? Pra cada 1 real investido eu tive X de lucro. (Lucro / cashback) |
| 3 | **A DEFINIR** | — |

### KPIs para análise Geral

- **A DEFINIR**

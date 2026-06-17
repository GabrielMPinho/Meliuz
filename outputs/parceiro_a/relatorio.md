# Relatorio A/B Cashback - parceiro_a

- Periodo: 2011-01-01 a 2011-04-02
- Total de dias: 92
- Grupos avaliados: grupo_1, grupo_2, grupo_3

## Decisao calculada

- Status: vencedor_definido
- Vencedor: grupo_1
- Motivo: consenso
- Recomendacao: Escalar grupo_1 para 100% do trafego.

## Tabela de KPIs

| Grupo | Elegivel | Lucro liquido | ROI | Lucro/comprador | GMV | Compradores | Cashback total | Margem GMV | Escala GMV | Escala compradores |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grupo_1 | sim | R$ 404.711,00 | 1,73x | R$ 42,01 | R$ 5.605.173,00 | 9.633 | R$ 233.424,00 | 7,2% | ok | ok |
| grupo_2 | sim | R$ 357.519,00 | 0,96x | R$ 33,06 | R$ 6.423.096,00 | 10.814 | R$ 370.659,00 | 5,6% | ok | ok |
| grupo_3 | sim | R$ 264.287,00 | 0,52x | R$ 23,16 | R$ 6.785.856,00 | 11.410 | R$ 503.600,00 | 3,9% | ok | ok |

## Graficos

### Lucro Liquido
![Lucro Liquido](graficos/lucro_liquido.png)

### ROI vs Lucro Liquido
![ROI vs Lucro Liquido](graficos/roi_vs_lucro.png)

### Composicao Comissao Cashback
![Composicao Comissao Cashback](graficos/composicao_comissao_cashback.png)

### Rentabilidade por Comprador
![Rentabilidade por Comprador](graficos/rentabilidade_por_comprador.png)

### Guardrails de Escala
![Guardrails de Escala](graficos/guardrails_escala.png)

### Sumário executivo
O vencedor definido é o **grupo_1**, e a recomendação final é: **Escalar grupo_1 para 100% do trafego.** A decisão se sustenta pelo consenso entre lucro e eficiência, com o grupo_1 liderando em lucro líquido, ROI e lucro por comprador, sem alertas de guardrail ou risco de escala.

### Lucro líquido total + ROI + Lucro por comprador + GMV
O **grupo_1** combina **R$ 404.711,00** de lucro líquido, **1,73x** de ROI e **R$ 42,01** de lucro por comprador, superando **grupo_2** e **grupo_3** em rentabilidade e retorno. Em GMV, o **grupo_1** registra **R$ 5.605.173,00**, abaixo de **grupo_2** e **grupo_3**, mas ainda com volume relevante para sustentar a decisão. Aqui, o trade-off principal é claro: o vencedor entrega melhor eficiência econômica sem depender do maior volume, o que favorece a escala com mais segurança.

### Lucro líquido total + GMV + Compradores totais
No recorte de volume, o **grupo_1** não lidera: **grupo_2** tem **R$ 6.423.096,00** de GMV e **10.814 compradores**, enquanto o **grupo_3** chega a **R$ 6.785.856,00** de GMV e **11.410 compradores**, ambos acima do vencedor. Ainda assim, o **grupo_1** mantém **R$ 404.711,00** de lucro líquido, que é o maior entre os três, mostrando que o resultado não depende de inflar volume para gerar retorno. Isso reforça que a decisão favorece o grupo com melhor qualidade de resultado, e não apenas o maior tamanho de base.

### ROI + Cashback total + Cashback sobre GMV
Na eficiência do incentivo, o **grupo_1** também é o melhor equilíbrio: tem **1,73x** de ROI, contra **0,96x** no **grupo_2** e **0,52x** no **grupo_3**. O **grupo_1** concentra **R$ 233.424,00** de cashback total e **4,2%** de cashback sobre GMV, abaixo do **grupo_2** (**R$ 370.659,00** e **5,8%**) e do **grupo_3** (**R$ 503.600,00** e **7,4%**). Isso indica que o vencedor gera mais retorno com menor pressão de incentivo, enquanto os demais grupos ficaram mais caros em cashback para entregar menor eficiência financeira.

### Riscos e limitações
Não há alertas de guardrail: todos os grupos estão elegíveis e com **escala_gmv = ok** e **escala_compradores = ok**, sem empate técnico e sem restrição de escalabilidade. O ranking também confirma a ordem do resultado, com **grupo_1** à frente de **grupo_2** e **grupo_3**, então a recomendação calculada não enfrenta limitações operacionais nos dados fornecidos.

### Próximo passo recomendado
Executar a ativação integral do **grupo_1** e monitorar sua manutenção de ROI e lucro líquido após a expansão para 100% do tráfego.

## Apendice de auditoria

### Blocos escolhidos pela LLM
- decisao_impacto_eficiencia_escala
- decisao_lucro_volume
- decisao_eficiencia_cashback

### Rankings dos KPIs de decisao

#### Ranking por Lucro liquido

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | R$ 404.711,00 | sim |
| 2 | grupo_2 | R$ 357.519,00 | sim |
| 3 | grupo_3 | R$ 264.287,00 | sim |

#### Ranking por ROI

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | 1,73x | sim |
| 2 | grupo_2 | 0,96x | sim |
| 3 | grupo_3 | 0,52x | sim |

#### Ranking por Lucro por comprador

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | R$ 42,01 | sim |
| 2 | grupo_2 | R$ 33,06 | sim |
| 3 | grupo_3 | R$ 23,16 | sim |

#### Ranking por GMV

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_3 | R$ 6.785.856,00 | sim |
| 2 | grupo_2 | R$ 6.423.096,00 | sim |
| 3 | grupo_1 | R$ 5.605.173,00 | sim |

#### Ranking por Compradores totais

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_3 | 11.410 | sim |
| 2 | grupo_2 | 10.814 | sim |
| 3 | grupo_1 | 9.633 | sim |

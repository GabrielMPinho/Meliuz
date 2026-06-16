# Relatorio A/B Cashback - parceiro_b

- Periodo: 2011-05-01 a 2011-06-30
- Total de dias: 61
- Grupos avaliados: grupo_1, grupo_2, grupo_3

## Decisao calculada

- Status: vencedor_definido
- Vencedor: grupo_1
- Motivo: consenso
- Recomendacao: Escalar grupo_1 para 100% do trafego.

## Tabela de KPIs

| Grupo | Elegivel | Lucro liquido | ROI | Lucro/comprador | GMV | Compradores | Cashback total | Margem GMV | Escala GMV | Escala compradores |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grupo_1 | sim | R$ 286.570,00 | 1,75x | R$ 35,87 | R$ 4.093.818,00 | 7.990 | R$ 163.751,00 | 7,0% | ok | ok |
| grupo_2 | sim | R$ 143.157,00 | 0,83x | R$ 26,26 | R$ 2.863.019,00 | 5.452 | R$ 171.778,00 | 5,0% | alerta | alerta |
| grupo_3 | sim | R$ 52.593,00 | 0,22x | R$ 10,46 | R$ 2.629.963,00 | 5.029 | R$ 236.697,00 | 2,0% | alerta | alerta |

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

**Sumário executivo**

O teste definiu **grupo_1** como vencedor, e a recomendação final é **"Escalar grupo_1 para 100% do trafego."** A decisão é sustentada pelo maior lucro líquido, maior ROI e melhor lucro por comprador entre os grupos elegíveis, sem alertas críticos em `decisao.alertas`.

**Lucro líquido total + ROI + Lucro por comprador + GMV**

O **grupo_1** combina o maior lucro líquido, com **R$ 286.570,00**, o maior ROI, com **1,75x**, e o maior lucro por comprador, com **R$ 35,87**, além de sustentar o maior GMV, de **R$ 4.093.818,00**. O **grupo_2** entrega menos lucro líquido, com **R$ 143.157,00**, ROI de **0,83x** e lucro por comprador de **R$ 26,26**, enquanto o **grupo_3** fica ainda abaixo, com **R$ 52.593,00**, ROI de **0,22x** e lucro por comprador de **R$ 10,46**. Esse bloco favorece claramente o grupo_1 porque ele é o único que junta impacto financeiro, eficiência e escala no mesmo patamar, sem depender de compensações entre volume e rentabilidade.

**Lucro líquido total + GMV + Compradores totais**

No eixo de volume, o **grupo_1** também lidera com **R$ 286.570,00** de lucro líquido, **R$ 4.093.818,00** de GMV e **7.990 compradores**. O **grupo_2** opera com volume menor, trazendo **R$ 143.157,00** de lucro, **R$ 2.863.019,00** de GMV e **5.452 compradores**, enquanto o **grupo_3** tem o menor volume e o menor retorno, com **R$ 52.593,00**, **R$ 2.629.963,00** e **5.029 compradores**. A leitura aqui é que o grupo_1 não venceu apenas por eficiência unitária: ele também foi o que converteu mais volume em lucro, então o resultado sustenta escala com retorno superior.

**ROI + Cashback total + Cashback sobre GMV**

Na eficiência do incentivo, o **grupo_1** mostra melhor uso do cashback, com **1,75x** de ROI, **R$ 163.751,00** de cashback total e **4,0%** de cashback sobre GMV. O **grupo_2** sobe o custo relativo do incentivo para **6,0%** do GMV e cai para **0,83x** de ROI, enquanto o **grupo_3** chega a **9,0%** do GMV em cashback e entrega apenas **0,22x** de ROI. Esse bloco explica por que os outros grupos perdem: o incentivo fica progressivamente mais caro e menos eficiente, e o grupo_1 é o único que preserva retorno positivo com melhor relação entre investimento e resultado.

**Lucro por comprador + Comissão por comprador + Cashback por comprador**

Na rentabilidade unitária, o **grupo_1** também fica à frente com **R$ 35,87** de lucro por comprador, **R$ 56,36** de comissão por comprador e **R$ 20,49** de cashback por comprador. O **grupo_2** cai para **R$ 26,26** de lucro por comprador, com cashback por comprador de **R$ 31,51**, e o **grupo_3** reduz ainda mais a geração de valor unitário, com **R$ 10,46** de lucro por comprador e **R$ 47,07** de cashback por comprador. O trade-off fica claro: quando o incentivo por comprador cresce sem retorno equivalente, a rentabilidade cai; por isso, mesmo sem ser o menor cashback por comprador, o grupo_1 é o mais saudável para escalar.

**Riscos e limitações**

Não há alertas em `decisao.alertas`, mas os guardrails mostram risco de escala em **grupo_2** e **grupo_3**, ambos com `escala_gmv` e `escala_compradores` em **alerta**. Como o vencedor foi definido por consenso e todos os grupos são elegíveis, não há empate técnico nem restrição de elegibilidade; ainda assim, os sinais de escala desfavoráveis nos grupos 2 e 3 reforçam que eles não entregam a mesma qualidade de expansão observada no grupo_1.

**Próximo passo recomendado**

Escalar o **grupo_1** para 100% do tráfego e monitorar a manutenção do ROI, do lucro líquido e dos guardrails de escala durante a expansão.

## Apendice de auditoria

### Blocos escolhidos pela LLM
- decisao_impacto_eficiencia_escala
- decisao_lucro_volume
- decisao_eficiencia_cashback
- decisao_rentabilidade_unitaria

### Rankings dos KPIs de decisao

#### Ranking por Lucro liquido

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | R$ 286.570,00 | sim |
| 2 | grupo_2 | R$ 143.157,00 | sim |
| 3 | grupo_3 | R$ 52.593,00 | sim |

#### Ranking por ROI

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | 1,75x | sim |
| 2 | grupo_2 | 0,83x | sim |
| 3 | grupo_3 | 0,22x | sim |

#### Ranking por Lucro por comprador

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | R$ 35,87 | sim |
| 2 | grupo_2 | R$ 26,26 | sim |
| 3 | grupo_3 | R$ 10,46 | sim |

#### Ranking por GMV

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | R$ 4.093.818,00 | sim |
| 2 | grupo_2 | R$ 2.863.019,00 | sim |
| 3 | grupo_3 | R$ 2.629.963,00 | sim |

#### Ranking por Compradores totais

| Posicao | Grupo | Valor | Elegivel |
| --- | --- | --- | --- |
| 1 | grupo_1 | 7.990 | sim |
| 2 | grupo_2 | 5.452 | sim |
| 3 | grupo_3 | 5.029 | sim |

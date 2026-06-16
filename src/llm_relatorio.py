def gerar_resposta_llm_simulada(json_auditavel):
    catalogo = json_auditavel["catalogo_blocos"]
    blocos_preferidos = [
        "decisao_impacto_eficiencia_escala",
        "decisao_lucro_volume",
        "decisao_eficiencia_cashback",
        "decisao_rentabilidade_unitaria",
    ]

    blocos_escolhidos = [
        bloco for bloco in blocos_preferidos
        if bloco in catalogo
    ][:4]

    if len(blocos_escolhidos) < 2:
        blocos_escolhidos = list(catalogo.keys())[:4]

    narrativa = montar_narrativa_markdown(
        json_auditavel,
        blocos_escolhidos,
    )

    return {
        "blocos_escolhidos": blocos_escolhidos,
        "narrativa_markdown": narrativa,
    }


def montar_narrativa_markdown(json_auditavel, blocos_escolhidos):
    decisao = json_auditavel["decisao"]
    catalogo = json_auditavel["catalogo_blocos"]

    secoes = [
        montar_sumario_executivo(json_auditavel),
    ]

    for bloco_id in blocos_escolhidos:
        bloco = catalogo[bloco_id]
        secoes.append(montar_secao_bloco(json_auditavel, bloco))

    secoes.extend([
        montar_riscos_limitacoes(json_auditavel),
        montar_proximo_passo(decisao),
    ])

    return "\n\n".join(secao for secao in secoes if secao)


def montar_sumario_executivo(json_auditavel):
    decisao = json_auditavel["decisao"]
    ranking = json_auditavel["ranking"]
    vencedor = decisao.get("vencedor")
    recomendacao = limpar_ponto_final(decisao.get("recomendacao"))

    if vencedor is None:
        return (
            "## Sumario executivo\n"
            f"A decisao calculada pelo Python foi: {recomendacao}. "
            "Nao escalar nenhum grupo neste teste, porque a regra deterministica "
            "nao encontrou uma combinacao saudavel de lucro_liquido, roi, "
            "lucro_por_comprador e escala."
        )

    grupo_referencia = ranking[0]["grupo"] if ranking else vencedor
    return (
        "## Sumario executivo\n"
        f"A decisao calculada pelo Python foi: {recomendacao}. "
        f"O vencedor definido foi {vencedor}; o ranking por lucro_liquido tem "
        f"{grupo_referencia} como primeira referencia financeira e a narrativa "
        "abaixo explica a decisao usando apenas KPIs auditados."
    )


def montar_secao_bloco(json_auditavel, bloco):
    linhas = [
        f"## {bloco['nome']}",
        (
            f"Este bloco usa os KPIs {', '.join(bloco['kpis_envolvidos'])} "
            f"para responder: {bloco['pergunta_que_responde']}"
        ),
    ]

    linhas.append("")
    linhas.append(interpretar_bloco(json_auditavel, bloco))
    linhas.append("")
    linhas.append("Valores de apoio:")

    for grupo, kpis in json_auditavel["kpis_por_grupo"].items():
        valores = [
            f"{kpi}: {formatar_kpi(kpi, kpis.get(kpi))}"
            for kpi in bloco["kpis_envolvidos"]
        ]
        elegivel = "elegivel" if json_auditavel["guardrails"][grupo]["elegivel"] else "inelegivel"
        linhas.append(f"- {grupo} ({elegivel}): " + "; ".join(valores) + ".")

    return "\n".join(linhas)


def interpretar_bloco(json_auditavel, bloco):
    bloco_id = bloco["id"]
    decisao = json_auditavel["decisao"]
    vencedor = decisao.get("vencedor")

    if vencedor is None:
        return (
            "A leitura deste bloco reforca que nenhum grupo deve ser escalado, "
            "porque a combinacao de indicadores nao sustenta uma recomendacao "
            "saudavel pela regra deterministica."
        )

    if bloco_id == "decisao_impacto_eficiencia_escala":
        return interpretar_impacto_eficiencia_escala(json_auditavel, vencedor)

    if bloco_id == "decisao_lucro_volume":
        return interpretar_lucro_volume(json_auditavel, vencedor)

    if bloco_id == "decisao_eficiencia_cashback":
        return interpretar_eficiencia_cashback(json_auditavel, vencedor)

    if bloco_id == "decisao_rentabilidade_unitaria":
        return interpretar_rentabilidade_unitaria(json_auditavel, vencedor)

    return interpretar_generico(json_auditavel, bloco, vencedor)


def interpretar_impacto_eficiencia_escala(json_auditavel, vencedor):
    kpis = json_auditavel["kpis_por_grupo"]
    vencedor_kpis = kpis[vencedor]
    lider_gmv = lider_por_metrica(kpis, "gmv")
    lider_compradores = lider_por_metrica(kpis, "total_compradores")

    leitura = (
        f"{vencedor} e a melhor opcao neste bloco porque combina o maior "
        f"lucro_liquido ({formatar_kpi('lucro_liquido', vencedor_kpis['lucro_liquido'])}), "
        f"o melhor roi ({formatar_kpi('roi', vencedor_kpis['roi'])}) e o maior "
        f"lucro_por_comprador ({formatar_kpi('lucro_por_comprador', vencedor_kpis['lucro_por_comprador'])})."
    )

    if lider_gmv != vencedor or lider_compradores != vencedor:
        leitura += (
            f" A escala absoluta fica mais forte em {lider_gmv} para gmv e em "
            f"{lider_compradores} para total_compradores, mas essa vantagem de "
            "volume nao compensou a perda de lucro e eficiencia frente ao vencedor."
        )
    else:
        leitura += (
            " Alem disso, o vencedor tambem sustenta a melhor escala do teste, "
            "o que reduz o trade-off entre resultado financeiro e volume."
        )

    return leitura


def interpretar_lucro_volume(json_auditavel, vencedor):
    kpis = json_auditavel["kpis_por_grupo"]
    vencedor_kpis = kpis[vencedor]
    lider_gmv = lider_por_metrica(kpis, "gmv")
    lider_compradores = lider_por_metrica(kpis, "total_compradores")

    leitura = (
        f"O bloco mostra que {vencedor} entrega o maior lucro_liquido "
        f"({formatar_kpi('lucro_liquido', vencedor_kpis['lucro_liquido'])}), "
        "que e o criterio financeiro principal da decisao."
    )

    if lider_gmv != vencedor or lider_compradores != vencedor:
        leitura += (
            f" O ponto de atencao e que {lider_gmv} lidera em gmv e "
            f"{lider_compradores} lidera em total_compradores; portanto, a "
            "decisao favorece rentabilidade sobre volume bruto."
        )
    else:
        leitura += (
            " Como o vencedor tambem lidera em volume, a decisao nao depende de "
            "abrir mao de escala para capturar lucro."
        )

    return leitura


def interpretar_eficiencia_cashback(json_auditavel, vencedor):
    kpis = json_auditavel["kpis_por_grupo"]
    vencedor_kpis = kpis[vencedor]
    menor_cashback = lider_por_metrica(kpis, "cashback_total", menor_melhor=True)
    menor_cashback_gmv = lider_por_metrica(
        kpis,
        "cashback_sobre_gmv",
        menor_melhor=True,
    )

    leitura = (
        f"{vencedor} sustenta a recomendacao porque transforma o incentivo em "
        f"retorno com roi de {formatar_kpi('roi', vencedor_kpis['roi'])}."
    )

    if menor_cashback == vencedor and menor_cashback_gmv == vencedor:
        leitura += (
            " Ele tambem tem o menor cashback_total e o menor cashback_sobre_gmv, "
            "indicando que o resultado nao dependeu de um incentivo mais caro."
        )
    else:
        leitura += (
            f" O menor cashback_total aparece em {menor_cashback} e o menor "
            f"cashback_sobre_gmv em {menor_cashback_gmv}, entao a leitura deve "
            "considerar custo do incentivo junto com o ROI."
        )

    return leitura


def interpretar_rentabilidade_unitaria(json_auditavel, vencedor):
    kpis = json_auditavel["kpis_por_grupo"]
    vencedor_kpis = kpis[vencedor]
    lider_comissao = lider_por_metrica(kpis, "comissao_por_comprador")
    menor_cashback = lider_por_metrica(
        kpis,
        "cashback_por_comprador",
        menor_melhor=True,
    )

    leitura = (
        f"Na unidade economica, {vencedor} se destaca por gerar "
        f"{formatar_kpi('lucro_por_comprador', vencedor_kpis['lucro_por_comprador'])} "
        "de lucro_por_comprador, mostrando que cada comprador deixa mais valor "
        "liquido depois do incentivo."
    )

    if lider_comissao != vencedor:
        leitura += (
            f" Mesmo sem liderar comissao_por_comprador, que fica com "
            f"{lider_comissao}, o vencedor protege melhor a margem porque "
            f"{menor_cashback} tem o menor cashback_por_comprador."
        )
    else:
        leitura += (
            " Como tambem lidera comissao_por_comprador, o resultado unitario "
            "fica alinhado com receita por comprador e controle do cashback."
        )

    return leitura


def interpretar_generico(json_auditavel, bloco, vencedor):
    kpis = json_auditavel["kpis_por_grupo"]
    lideres = [
        f"{kpi}: {lider_por_metrica(kpis, kpi)}"
        for kpi in bloco["kpis_envolvidos"]
        if kpi in kpis[vencedor] and kpis[vencedor][kpi] is not None
    ]

    return (
        f"A leitura comparativa favorece {vencedor} quando estes indicadores "
        "sao avaliados junto com a regra de decisao. Lideres por KPI no bloco: "
        + "; ".join(lideres)
        + "."
    )


def lider_por_metrica(kpis_por_grupo, metrica, menor_melhor=False):
    grupos_validos = [
        grupo for grupo, kpis in kpis_por_grupo.items()
        if kpis.get(metrica) is not None
    ]

    if not grupos_validos:
        return "indisponivel"

    return sorted(
        grupos_validos,
        key=lambda grupo: kpis_por_grupo[grupo][metrica],
        reverse=not menor_melhor,
    )[0]


def montar_riscos_limitacoes(json_auditavel):
    decisao = json_auditavel["decisao"]
    linhas = ["## Riscos e limitacoes"]

    alertas = decisao.get("alertas", [])
    if alertas:
        for alerta in alertas:
            linhas.append(f"- {alerta}")
    else:
        linhas.append("- Nao ha alertas adicionais na decisao calculada.")

    if decisao.get("empate_tecnico"):
        linhas.append(
            "- Existe empate tecnico ou diferenca pequena entre os candidatos "
            "avaliados pela regra."
        )

    if decisao.get("motivo") == "unico_elegivel":
        linhas.append(
            "- Apenas um grupo foi elegivel; a decisao deve ser lida com essa "
            "limitacao."
        )

    guardrails_com_risco = False
    for grupo, guardrail in json_auditavel["guardrails"].items():
        escala_gmv = guardrail["escala_gmv"]
        escala_compradores = guardrail["escala_compradores"]

        if escala_gmv in ["alerta", "critico"] or escala_compradores in [
            "alerta",
            "critico",
        ]:
            guardrails_com_risco = True
            linhas.append(
                f"- {grupo} tem risco de escala: escala_gmv={escala_gmv}; "
                f"escala_compradores={escala_compradores}."
            )

    if not guardrails_com_risco:
        linhas.append(
            "- Nao ha guardrail de escala em alerta ou critico para os grupos."
        )

    return "\n".join(linhas)


def montar_proximo_passo(decisao):
    if decisao.get("vencedor") is None:
        proximo = (
            "Revisar a politica de cashback e redesenhar o teste antes de "
            "tentar escalar uma variante."
        )
    else:
        proximo = (
            "Aplicar a recomendacao calculada em uma proxima janela controlada "
            "e monitorar lucro_liquido, roi, lucro_por_comprador e escala."
        )

    return "## Proximo passo recomendado\n" + proximo


def limpar_ponto_final(texto):
    if texto is None:
        return ""

    return str(texto).strip().rstrip(".")


def formatar_kpi(kpi, valor):
    if valor is None:
        return "indisponivel"

    if kpi in {
        "lucro_liquido",
        "gmv",
        "comissao_total",
        "cashback_total",
        "ticket_medio",
        "comissao_por_comprador",
        "cashback_por_comprador",
        "lucro_por_comprador",
    }:
        return formatar_moeda(valor)

    if kpi == "roi":
        return formatar_decimal(valor) + "x"

    if kpi in {
        "margem_liquida_gmv",
        "cashback_sobre_gmv",
        "perda_gmv_maior_grupo",
        "perda_compradores_maior_grupo",
    }:
        return formatar_percentual(valor)

    if kpi in {"total_compradores", "dias_lucro_negativo"}:
        return formatar_inteiro(valor)

    return str(valor)


def formatar_moeda(valor):
    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor):
    return formatar_decimal(valor * 100, casas=1) + "%"


def formatar_decimal(valor, casas=2):
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_inteiro(valor):
    return f"{int(round(valor)):,.0f}".replace(",", ".")

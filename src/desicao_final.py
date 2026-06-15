def decisao_final(df):
    try:
        from kpis_decisao import kpis_decisao
        from kpis_analise import kpis_analise
    except ModuleNotFoundError:
        from src.kpis_decisao import kpis_decisao
        from src.kpis_analise import kpis_analise

    # ------------------------ PARAMETROS ------------------------------------
    LUCRO_TOLERANCE = 0.10
    ROI_ADVANTAGE = 0.20
    EMPATE_LUCRO = 0.05
    EMPATE_ROI = 0.10
    SCALE_OK_LIMIT = 0.20
    SCALE_CRITICAL_LIMIT = 0.40

    # ------------------------ FUNCOES ---------------------------------------
    def valor_valido(valor):
        return valor is not None

    def dividir_seguro(numerador, denominador):
        if denominador is None or denominador == 0:
            return None
        return numerador / denominador

    def escala_critica(kpis_grupo):
        perda_gmv = kpis_grupo["perda_gmv_maior_grupo"]
        perda_compradores = kpis_grupo["perda_compradores_maior_grupo"]

        return (
            perda_gmv is not None
            and perda_gmv > SCALE_CRITICAL_LIMIT
        ) or (
            perda_compradores is not None
            and perda_compradores > SCALE_CRITICAL_LIMIT
        )

    def escala_alerta(kpis_grupo):
        perda_gmv = kpis_grupo["perda_gmv_maior_grupo"]
        perda_compradores = kpis_grupo["perda_compradores_maior_grupo"]

        alerta_gmv = (
            perda_gmv is not None
            and SCALE_OK_LIMIT < perda_gmv <= SCALE_CRITICAL_LIMIT
        )

        alerta_compradores = (
            perda_compradores is not None
            and SCALE_OK_LIMIT < perda_compradores <= SCALE_CRITICAL_LIMIT
        )

        return alerta_gmv or alerta_compradores

    def grupo_elegivel(kpis_decisao_grupo, kpis_analise_grupo):
        lucro = kpis_decisao_grupo["lucro_liquido"]
        roi = kpis_decisao_grupo["roi"]
        lucro_por_comprador = kpis_decisao_grupo["lucro_por_comprador"]

        criterios_financeiros = (
            valor_valido(lucro)
            and valor_valido(roi)
            and valor_valido(lucro_por_comprador)
            and lucro > 0
            and roi > 0
            and lucro_por_comprador > 0
        )

        return criterios_financeiros and not escala_critica(kpis_analise_grupo)

    def maior_grupo_por_metrica(grupos, kpis, metrica):
        return max(grupos, key=lambda grupo: kpis[grupo][metrica])

    def calcular_gap(valor_a, valor_b):
        # Regra do resumo: gap relativo ao maior valor entre os dois candidatos.
        maior_valor = max(valor_a, valor_b)
        return dividir_seguro(abs(valor_a - valor_b), maior_valor)

    def existe_empate_tecnico(candidato_lucro, candidato_eficiencia, kpis):
        lucro_a = kpis[candidato_lucro]["lucro_liquido"]
        lucro_b = kpis[candidato_eficiencia]["lucro_liquido"]
        roi_a = kpis[candidato_lucro]["roi"]
        roi_b = kpis[candidato_eficiencia]["roi"]

        gap_lucro = calcular_gap(lucro_a, lucro_b)
        gap_roi = calcular_gap(roi_a, roi_b)

        empate_tecnico = (
            gap_lucro is not None
            and gap_roi is not None
            and gap_lucro < EMPATE_LUCRO
            and gap_roi < EMPATE_ROI
        )

        return empate_tecnico, gap_lucro, gap_roi

    def desempatar(candidato_lucro, candidato_eficiencia, kpis):
        criterios = [
            "lucro_por_comprador",
            "gmv",
            "total_compradores",
        ]

        for criterio in criterios:
            valor_lucro = kpis[candidato_lucro][criterio]
            valor_eficiencia = kpis[candidato_eficiencia][criterio]

            if valor_lucro > valor_eficiencia:
                return candidato_lucro, criterio

            if valor_eficiencia > valor_lucro:
                return candidato_eficiencia, criterio

        return candidato_lucro, "lucro_liquido"

    def gerar_alertas(vencedor, motivo, empate_tecnico, analise, candidatos, kpis):
        alertas = []

        if empate_tecnico:
            alertas.append(
                "Diferenca pequena demais entre "
                f"{candidatos['candidato_lucro']} e "
                f"{candidatos['candidato_eficiencia']} para sustentar "
                "recomendacao forte com dados agregados."
            )

        if motivo == "eficiencia":
            alertas.append(
                "Candidato de ROI venceu mesmo sem ter o maior lucro."
            )

        if motivo == "lucro":
            roi_vencedor = kpis[vencedor]["roi"]
            melhor_roi = kpis[candidatos["candidato_eficiencia"]]["roi"]

            if (
                roi_vencedor is not None
                and melhor_roi is not None
                and melhor_roi > 0
                and roi_vencedor < melhor_roi * (1 - ROI_ADVANTAGE)
            ):
                alertas.append(
                    "Vencedor tem ROI muito abaixo do melhor ROI do teste."
                )

        if escala_alerta(analise[vencedor]):
            alertas.append(
                "Vencedor possui risco de escala entre 20% e 40%."
            )

        return alertas

    # ------------------------ CALCULANDO -------------------------------------
    kpis_dec = kpis_decisao(df)
    kpis_anl = kpis_analise(df)

    grupos_elegiveis = []
    elegibilidade = {}

    for grupo in kpis_dec.keys():
        elegivel = grupo_elegivel(kpis_dec[grupo], kpis_anl[grupo])
        elegibilidade[grupo] = elegivel

        if elegivel:
            grupos_elegiveis.append(grupo)

    # ------------------------ SEM ELEGIVEIS ----------------------------------
    if not grupos_elegiveis:
        return {
            "status": "sem_grupo_elegivel",
            "vencedor": None,
            "recomendacao": "Nao escalar. Revisar politica de cashback.",
            "motivo": "nenhum grupo passou nos criterios de elegibilidade",
            "elegibilidade": elegibilidade,
            "alertas": [
                "Nenhum grupo apresentou combinacao saudavel de lucro, ROI, lucro por comprador e escala."
            ],
        }

    if len(grupos_elegiveis) == 1:
        vencedor = grupos_elegiveis[0]
        alertas = gerar_alertas(
            vencedor,
            "unico_elegivel",
            False,
            kpis_anl,
            {
                "candidato_lucro": vencedor,
                "candidato_eficiencia": vencedor,
            },
            kpis_dec,
        )

        alertas.append(
            "Apenas um grupo passou nos criterios de elegibilidade."
        )

        return {
            "status": "vencedor_definido",
            "vencedor": vencedor,
            "recomendacao": f"Escalar {vencedor} para 100% do trafego.",
            "motivo": "unico_elegivel",
            "criterio_desempate": None,
            "candidatos": {
                "candidato_lucro": vencedor,
                "candidato_eficiencia": vencedor,
            },
            "empate_tecnico": False,
            "gap_lucro": None,
            "gap_roi": None,
            "elegibilidade": elegibilidade,
            "alertas": alertas,
            "kpis_vencedor": kpis_dec[vencedor],
        }

    # ------------------------ DECISAO ----------------------------------------
    candidato_lucro = maior_grupo_por_metrica(
        grupos_elegiveis, kpis_dec, "lucro_liquido"
    )

    candidato_eficiencia = maior_grupo_por_metrica(
        grupos_elegiveis, kpis_dec, "roi"
    )

    candidatos = {
        "candidato_lucro": candidato_lucro,
        "candidato_eficiencia": candidato_eficiencia,
    }

    empate_tecnico = False
    criterio_desempate = None
    gap_lucro = None
    gap_roi = None

    if candidato_lucro == candidato_eficiencia:
        vencedor = candidato_lucro
        motivo = "consenso"

    else:
        lucro_a = kpis_dec[candidato_lucro]["lucro_liquido"]
        lucro_b = kpis_dec[candidato_eficiencia]["lucro_liquido"]
        roi_a = kpis_dec[candidato_lucro]["roi"]
        roi_b = kpis_dec[candidato_eficiencia]["roi"]

        troca_por_eficiencia = (
            lucro_b >= lucro_a * (1 - LUCRO_TOLERANCE)
            and roi_b >= roi_a * (1 + ROI_ADVANTAGE)
        )

        if troca_por_eficiencia:
            vencedor = candidato_eficiencia
            motivo = "eficiencia"

        else:
            empate_tecnico, gap_lucro, gap_roi = existe_empate_tecnico(
                candidato_lucro, candidato_eficiencia, kpis_dec
            )

            if empate_tecnico:
                vencedor, criterio_desempate = desempatar(
                    candidato_lucro, candidato_eficiencia, kpis_dec
                )
                motivo = "desempate_tecnico"

            else:
                vencedor = candidato_lucro
                motivo = "lucro"

    alertas = gerar_alertas(
        vencedor, motivo, empate_tecnico, kpis_anl, candidatos, kpis_dec
    )

    # ------------------------ ENTREGANDO -------------------------------------
    return {
        "status": "vencedor_definido",
        "vencedor": vencedor,
        "recomendacao": f"Escalar {vencedor} para 100% do trafego.",
        "motivo": motivo,
        "criterio_desempate": criterio_desempate,
        "candidatos": candidatos,
        "empate_tecnico": empate_tecnico,
        "gap_lucro": gap_lucro,
        "gap_roi": gap_roi,
        "elegibilidade": elegibilidade,
        "alertas": alertas,
        "kpis_vencedor": kpis_dec[vencedor],
    }


def desicao_final(df):
    return decisao_final(df)

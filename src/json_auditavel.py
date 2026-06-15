def gerar_json_auditavel(df):
    try:
        from kpis_decisao import kpis_decisao
        from kpis_analise import kpis_analise
        from desicao_final import decisao_final
    except ModuleNotFoundError:
        from src.kpis_decisao import kpis_decisao
        from src.kpis_analise import kpis_analise
        from src.desicao_final import decisao_final

    import math

    SCALE_OK_LIMIT = 0.20
    SCALE_CRITICAL_LIMIT = 0.40

    def converter_tipo(valor):
        if isinstance(valor, dict):
            return {
                str(chave): converter_tipo(valor_chave)
                for chave, valor_chave in valor.items()
            }

        if isinstance(valor, list):
            return [converter_tipo(item) for item in valor]

        if hasattr(valor, "item") and not isinstance(valor, (str, bytes)):
            try:
                valor = valor.item()
            except ValueError:
                pass

        if isinstance(valor, float) and math.isnan(valor):
            return None

        return valor

    def classificar_escala(perda):
        if perda is None:
            return "ok"

        if perda <= SCALE_OK_LIMIT:
            return "ok"

        if perda <= SCALE_CRITICAL_LIMIT:
            return "alerta"

        return "critico"

    def calcular_gap_lucro_segundo(ranking):
        if len(ranking) < 2:
            return None

        lucro_primeiro = ranking[0]["lucro_liquido"]
        lucro_segundo = ranking[1]["lucro_liquido"]

        if lucro_primeiro is None or lucro_primeiro == 0:
            return None

        return abs(lucro_primeiro - lucro_segundo) / lucro_primeiro

    def montar_catalogo_blocos():
        return {
            "decisao_impacto_eficiencia_escala": {
                "id": "decisao_impacto_eficiencia_escala",
                "nome": "Lucro liquido total + ROI + Lucro por comprador + GMV",
                "kpis_envolvidos": [
                    "lucro_liquido",
                    "roi",
                    "lucro_por_comprador",
                    "gmv",
                ],
                "pergunta_que_responde": (
                    "O grupo combina impacto financeiro, eficiencia, "
                    "rentabilidade unitaria e escala?"
                ),
            },
            "decisao_lucro_volume": {
                "id": "decisao_lucro_volume",
                "nome": "Lucro liquido total + GMV + Compradores totais",
                "kpis_envolvidos": [
                    "lucro_liquido",
                    "gmv",
                    "total_compradores",
                ],
                "pergunta_que_responde": (
                    "O lucro veio mantendo volume relevante?"
                ),
            },
            "decisao_eficiencia_cashback": {
                "id": "decisao_eficiencia_cashback",
                "nome": "ROI + Cashback total + Cashback sobre GMV",
                "kpis_envolvidos": [
                    "roi",
                    "cashback_total",
                    "cashback_sobre_gmv",
                ],
                "pergunta_que_responde": (
                    "O cashback investido foi eficiente ou caro demais?"
                ),
            },
            "decisao_rentabilidade_unitaria": {
                "id": "decisao_rentabilidade_unitaria",
                "nome": (
                    "Lucro por comprador + Comissao por comprador + "
                    "Cashback por comprador"
                ),
                "kpis_envolvidos": [
                    "lucro_por_comprador",
                    "comissao_por_comprador",
                    "cashback_por_comprador",
                ],
                "pergunta_que_responde": (
                    "Cada comprador gera valor suficiente depois do incentivo?"
                ),
            },
            "decisao_origem_volume": {
                "id": "decisao_origem_volume",
                "nome": "GMV + Compradores totais + Ticket medio",
                "kpis_envolvidos": [
                    "gmv",
                    "total_compradores",
                    "ticket_medio",
                ],
                "pergunta_que_responde": (
                    "O volume veio de muitos compradores ou de compras maiores?"
                ),
            },
            "analise_conversao_gmv_lucro": {
                "id": "analise_conversao_gmv_lucro",
                "nome": "GMV + Margem liquida sobre GMV + Lucro liquido total",
                "kpis_envolvidos": [
                    "gmv",
                    "margem_liquida_gmv",
                    "lucro_liquido",
                ],
                "pergunta_que_responde": (
                    "O grupo vende muito e transforma esse volume em lucro?"
                ),
            },
            "analise_custo_incentivo": {
                "id": "analise_custo_incentivo",
                "nome": "Cashback total + Cashback sobre GMV + ROI",
                "kpis_envolvidos": [
                    "cashback_total",
                    "cashback_sobre_gmv",
                    "roi",
                ],
                "pergunta_que_responde": (
                    "O incentivo foi caro demais ou eficiente?"
                ),
            },
            "analise_tradeoff_lucro_roi_gmv": {
                "id": "analise_tradeoff_lucro_roi_gmv",
                "nome": "Lucro liquido total + ROI + GMV",
                "kpis_envolvidos": [
                    "lucro_liquido",
                    "roi",
                    "gmv",
                ],
                "pergunta_que_responde": (
                    "O resultado combina impacto financeiro, eficiencia e escala?"
                ),
            },
        }

    kpis_dec = kpis_decisao(df)
    kpis_anl = kpis_analise(df)
    decisao = decisao_final(df)

    grupos = list(kpis_dec.keys())

    data_inicio = df["data"].min()
    data_fim = df["data"].max()

    metadados = {
        "parceiro": str(df["parceiro"].dropna().unique()[0]),
        "periodo_inicio": data_inicio.strftime("%Y-%m-%d"),
        "periodo_fim": data_fim.strftime("%Y-%m-%d"),
        "total_dias": int(df["data"].nunique()),
        "grupos": [str(grupo) for grupo in grupos],
    }

    kpis_por_grupo = {}
    for grupo in grupos:
        kpis_por_grupo[grupo] = {
            **kpis_dec[grupo],
            **kpis_anl[grupo],
        }

    ranking = []
    for grupo in grupos:
        ranking.append({
            "grupo": grupo,
            "lucro_liquido": kpis_dec[grupo]["lucro_liquido"],
            "roi": kpis_dec[grupo]["roi"],
            "elegivel": decisao["elegibilidade"][grupo],
        })

    ranking = sorted(
        ranking,
        key=lambda item: item["lucro_liquido"],
        reverse=True,
    )

    decisao = converter_tipo(decisao)
    decisao["gap_lucro_segundo"] = converter_tipo(
        calcular_gap_lucro_segundo(ranking)
    )

    guardrails = {}
    for grupo in grupos:
        guardrails[grupo] = {
            "escala_gmv": classificar_escala(
                kpis_anl[grupo]["perda_gmv_maior_grupo"]
            ),
            "escala_compradores": classificar_escala(
                kpis_anl[grupo]["perda_compradores_maior_grupo"]
            ),
            "elegivel": decisao["elegibilidade"][grupo],
        }

    json_auditavel = {
        "metadados": metadados,
        "kpis_por_grupo": kpis_por_grupo,
        "decisao": decisao,
        "ranking": ranking,
        "guardrails": guardrails,
        "alertas": decisao["alertas"],
        "catalogo_blocos": montar_catalogo_blocos(),
    }

    return converter_tipo(json_auditavel)

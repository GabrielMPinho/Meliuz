def kpis_analise(df):
    import pandas as pd

    #----------------------KPIs-------------------------------------

    def calcular_comissao_total(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            comissao_total = linha["comissão"]
            resultado[grupo] = comissao_total
        return resultado

    def calcular_cashback_total(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            cashback_total = linha["cashback"]
            resultado[grupo] = cashback_total
        return resultado

    def calcular_ticket_medio(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            ticket_medio = linha["vendas_totais"] / linha["compradores"]
            resultado[grupo] = ticket_medio
        return resultado

    def calcular_comissao_por_comprador(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            comissao_por_comprador = linha["comissão"] / linha["compradores"]
            resultado[grupo] = comissao_por_comprador
        return resultado

    def calcular_cashback_por_comprador(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            cashback_por_comprador = linha["cashback"] / linha["compradores"]
            resultado[grupo] = cashback_por_comprador
        return resultado

    def calcular_margem_liquida_gmv(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            lucro_liquido = linha["comissão"] - linha["cashback"]
            margem_liquida_gmv = lucro_liquido / linha["vendas_totais"]
            resultado[grupo] = margem_liquida_gmv
        return resultado

    def calcular_cashback_sobre_gmv(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            cashback_sobre_gmv = linha["cashback"] / linha["vendas_totais"]
            resultado[grupo] = cashback_sobre_gmv
        return resultado

    def calcular_perda_gmv_maior_grupo(df_agrupado):
        resultado = {}
        gmvs = {}
        for grupo, linha in df_agrupado.iterrows():
            gmvs[grupo] = linha["vendas_totais"]
        maior_gmv = max(gmvs.values())
        for grupo, linha in df_agrupado.iterrows():
            perda_gmv = (maior_gmv - linha["vendas_totais"]) / maior_gmv
            resultado[grupo] = perda_gmv
        return resultado

    def calcular_perda_compradores_maior_grupo(df_agrupado):
        resultado = {}
        compradores_por_grupo = {}
        for grupo, linha in df_agrupado.iterrows():
            compradores_por_grupo[grupo] = linha["compradores"]
        maior_compradores = max(compradores_por_grupo.values())
        for grupo, linha in df_agrupado.iterrows():
            perda_compradores = (maior_compradores - linha["compradores"]) / maior_compradores
            resultado[grupo] = perda_compradores
        return resultado

    def calcular_dias_lucro_negativo(df_original):
        resultado = {}

        for grupo in df_original["grupos_de_usuários"].unique():
            df_grupo = df_original[
                df_original["grupos_de_usuários"] == grupo
            ]

            dias_negativos = (
                (df_grupo["comissão"] - df_grupo["cashback"]) < 0
            ).sum()

            resultado[grupo] = int(dias_negativos)

        return resultado

    #-----------------------Verificação---------------------------------------
    colunas_esperadas = [
        "data", "grupos_de_usuários", "parceiro",
        "compradores", "comissão", "cashback", "vendas_totais",
    ]
    for coluna in df.columns:
        if coluna not in colunas_esperadas:
            raise ValueError(f"Coluna inesperada: {coluna}")

    #----------------------Agrupamento-------------------------------------
    df_agrupado = df.groupby("grupos_de_usuários").agg({
        "comissão": "sum",
        "cashback": "sum",
        "compradores": "sum",
        "vendas_totais": "sum"
    })

    #------------------------Calculando----------------------------------------

    comissao_total_por_grp = calcular_comissao_total(df_agrupado)
    cashback_total_por_grp = calcular_cashback_total(df_agrupado)
    ticket_medio_por_grp = calcular_ticket_medio(df_agrupado)
    comissao_por_comprador_por_grp = calcular_comissao_por_comprador(df_agrupado)
    cashback_por_comprador_por_grp = calcular_cashback_por_comprador(df_agrupado)
    margem_liquida_gmv_por_grp = calcular_margem_liquida_gmv(df_agrupado)
    cashback_sobre_gmv_por_grp = calcular_cashback_sobre_gmv(df_agrupado)
    perda_gmv_maior_grupo_por_grp = calcular_perda_gmv_maior_grupo(df_agrupado)
    perda_compradores_maior_grupo_por_grp = calcular_perda_compradores_maior_grupo(df_agrupado)
    dias_lucro_negativo_por_grp = calcular_dias_lucro_negativo(df)

    #------------------------Entregando----------------------------------------
    entrega_kpis_analise = {}
    for grupo in df_agrupado.index:
        entrega_kpis_analise[grupo] = {
            "comissao_total": comissao_total_por_grp[grupo],
            "cashback_total": cashback_total_por_grp[grupo],
            "ticket_medio": ticket_medio_por_grp[grupo],
            "comissao_por_comprador": comissao_por_comprador_por_grp[grupo],
            "cashback_por_comprador": cashback_por_comprador_por_grp[grupo],
            "margem_liquida_gmv": margem_liquida_gmv_por_grp[grupo],
            "cashback_sobre_gmv": cashback_sobre_gmv_por_grp[grupo],
            "perda_gmv_maior_grupo": perda_gmv_maior_grupo_por_grp[grupo],
            "perda_compradores_maior_grupo": perda_compradores_maior_grupo_por_grp[grupo],
            "dias_lucro_negativo": dias_lucro_negativo_por_grp[grupo]
        }
    return entrega_kpis_analise

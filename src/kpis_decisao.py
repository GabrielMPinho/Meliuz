def kpis_decisao(df):
    import pandas as pd

    #----------------------KPIs-------------------------------------

    def dividir_seguro(numerador, denominador):
        if pd.isna(denominador) or denominador == 0:
            return None
        return numerador / denominador

    def calcular_lucro_liquido(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            lucro = linha["comissão"] - linha["cashback"]
            resultado[grupo] = lucro
        return resultado
    
    def calcular_roi(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            lucro = linha["comissão"] - linha["cashback"]
            roi = dividir_seguro(lucro, linha["cashback"])
            resultado[grupo] = roi
        return resultado
    
    def calcular_lucro_por_comprador(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            lucro = linha["comissão"] - linha["cashback"]
            lucro_comprador = dividir_seguro(lucro, linha["compradores"])
            resultado[grupo] = lucro_comprador
        return resultado
    
    def calcular_gmv(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            resultado[grupo] = linha["vendas_totais"]
        return resultado
    
    def calcular_total_compradores(df_agrupado):
        resultado = {}
        for grupo, linha in df_agrupado.iterrows():
            resultado[grupo] = linha["compradores"]
        return resultado
    
    #-----------------------Verificaçãp---------------------------------------
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

    lucro_liquido_por_grp = calcular_lucro_liquido(df_agrupado)
    roi_por_grp = calcular_roi(df_agrupado)
    lucro_por_comprador_por_grp = calcular_lucro_por_comprador(df_agrupado)
    total_vendas_por_grp = calcular_gmv(df_agrupado)
    total_compradores_por_grp = calcular_total_compradores(df_agrupado)

    #------------------------Entregando----------------------------------------
    entrega_kpis_desicao = {}
    for grupo in df_agrupado.index:
        entrega_kpis_desicao[grupo] = {
            "lucro_liquido": lucro_liquido_por_grp[grupo],
            "roi": roi_por_grp[grupo],
            "lucro_por_comprador": lucro_por_comprador_por_grp[grupo],
            "gmv": total_vendas_por_grp[grupo],
            "total_compradores": total_compradores_por_grp[grupo]
        }
    return entrega_kpis_desicao


















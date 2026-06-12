def data_cleaning(caminho):
    import pandas as pd
    # ------------------------- FUNÇÕES -----------------------
    # Tratando colunas dinheiro
    def tratamento_monetario(coluna):
        df[f"{coluna}"] = (
            df[f"{coluna}"]
            .str.replace("$", "")
            .str.replace(".", "")
            .str.strip()
            .str.replace("R", "")
        )

        # Transformando numeros em int
        df[f"{coluna}"] = pd.to_numeric(df[f"{coluna}"], errors="coerce")
        return df[coluna]

    # Tratando colunas str
    def tratamento_string(coluna):
        df[f"{coluna}"] = (
            df[f"{coluna}"]
            .str.lower()
            .str.strip()
            .str.replace(" ", "_")
        )
    #-----------------------------------------------------------
    
    df_ini = pd.read_csv(f"{caminho}")
    df = df_ini.copy(deep=True)

    # Verificar se tem as colunas esperadas
    colunas_esperadas = [
        "data",
        "grupos_de_usuários",
        "parceiro",
        "compradores",
        "comissão",
        "cashback",
        "vendas_totais",
    ]
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    for coluna in df.columns:
        if coluna not in colunas_esperadas:
            raise ValueError(f"Coluna inesperada: {coluna}")
    #-----------------------------------------------------------

    # Tratando colunas
    tratamento_monetario("comissão")
    tratamento_monetario("cashback")
    tratamento_monetario("vendas_totais")
    tratamento_string("grupos_de_usuários")
    tratamento_string("parceiro")
    df["compradores"] = pd.to_numeric(df["compradores"], errors="coerce")    
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    #-----------------------------------------------------------
    
    if df.isna().any().any():
        colunas_texto = ["grupos_de_usuários", "parceiro"]
        colunas_numericas = ["compradores", "comissão", "cashback", "vendas_totais"]

        df[colunas_texto] = df[colunas_texto].fillna("NULL")
        df[colunas_numericas] = df[colunas_numericas].fillna(0)
        df["data"] = df["data"].fillna(pd.NaT)

    return df

from pathlib import Path


def salvar_relatorio_markdown(
    json_auditavel,
    resposta_llm,
    graficos_resultado,
    caminho_saida,
):
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    conteudo = montar_relatorio_markdown(
        json_auditavel,
        resposta_llm,
        graficos_resultado,
        caminho_saida.parent,
    )

    caminho_saida.write_text(conteudo, encoding="utf-8")
    return str(caminho_saida)


def montar_relatorio_markdown(
    json_auditavel,
    resposta_llm,
    graficos_resultado,
    diretorio_relatorio,
):
    metadados = json_auditavel["metadados"]
    decisao = json_auditavel["decisao"]

    secoes = [
        montar_cabecalho(metadados),
        montar_decisao(decisao),
        montar_tabela_kpis(json_auditavel),
        montar_graficos(graficos_resultado, diretorio_relatorio),
        resposta_llm["narrativa_markdown"],
        montar_apendice_auditoria(json_auditavel, resposta_llm),
    ]

    return "\n\n".join(secao for secao in secoes if secao) + "\n"


def montar_cabecalho(metadados):
    return "\n".join([
        f"# Relatorio A/B Cashback - {metadados['parceiro']}",
        "",
        f"- Periodo: {metadados['periodo_inicio']} a {metadados['periodo_fim']}",
        f"- Total de dias: {metadados['total_dias']}",
        f"- Grupos avaliados: {', '.join(metadados['grupos'])}",
    ])


def montar_decisao(decisao):
    vencedor = decisao.get("vencedor") or "sem vencedor"
    alertas = decisao.get("alertas", [])

    linhas = [
        "## Decisao calculada",
        "",
        f"- Status: {decisao.get('status')}",
        f"- Vencedor: {vencedor}",
        f"- Motivo: {decisao.get('motivo')}",
        f"- Recomendacao: {decisao.get('recomendacao')}",
    ]

    if decisao.get("criterio_desempate"):
        linhas.append(f"- Criterio de desempate: {decisao['criterio_desempate']}")

    if decisao.get("gap_lucro") is not None:
        linhas.append(f"- Gap de lucro: {formatar_percentual(decisao['gap_lucro'])}")

    if decisao.get("gap_roi") is not None:
        linhas.append(f"- Gap de ROI: {formatar_percentual(decisao['gap_roi'])}")

    if alertas:
        linhas.append("- Alertas:")
        linhas.extend(f"  - {alerta}" for alerta in alertas)

    return "\n".join(linhas)


def montar_tabela_kpis(json_auditavel):
    cabecalho = [
        "Grupo",
        "Elegivel",
        "Lucro liquido",
        "ROI",
        "Lucro/comprador",
        "GMV",
        "Compradores",
        "Cashback total",
        "Margem GMV",
        "Escala GMV",
        "Escala compradores",
    ]

    linhas = [
        "## Tabela de KPIs",
        "",
        "| " + " | ".join(cabecalho) + " |",
        "| " + " | ".join(["---"] * len(cabecalho)) + " |",
    ]

    for grupo, kpis in json_auditavel["kpis_por_grupo"].items():
        guardrail = json_auditavel["guardrails"][grupo]
        linha = [
            grupo,
            "sim" if guardrail["elegivel"] else "nao",
            formatar_moeda(kpis.get("lucro_liquido")),
            formatar_roi(kpis.get("roi")),
            formatar_moeda(kpis.get("lucro_por_comprador")),
            formatar_moeda(kpis.get("gmv")),
            formatar_inteiro(kpis.get("total_compradores")),
            formatar_moeda(kpis.get("cashback_total")),
            formatar_percentual(kpis.get("margem_liquida_gmv")),
            guardrail["escala_gmv"],
            guardrail["escala_compradores"],
        ]
        linhas.append("| " + " | ".join(linha) + " |")

    return "\n".join(linhas)


def montar_graficos(graficos_resultado, diretorio_relatorio):
    arquivos = graficos_resultado.get("arquivos", []) if graficos_resultado else []

    if not arquivos:
        return "## Graficos\n\nNenhum grafico foi gerado."

    linhas = ["## Graficos", ""]
    diretorio_relatorio = Path(diretorio_relatorio)

    for arquivo in arquivos:
        caminho = Path(arquivo)
        try:
            caminho_relativo = caminho.relative_to(diretorio_relatorio)
        except ValueError:
            caminho_relativo = caminho

        caminho_markdown = caminho_relativo.as_posix()
        titulo = titulo_grafico(caminho.stem)
        linhas.append(f"### {titulo}")
        linhas.append(f"![{titulo}]({caminho_markdown})")
        linhas.append("")

    avisos = graficos_resultado.get("avisos", []) if graficos_resultado else []
    if avisos:
        linhas.append("### Avisos dos graficos")
        linhas.extend(f"- {aviso}" for aviso in avisos)

    return "\n".join(linhas).strip()


def titulo_grafico(nome):
    titulos = {
        "lucro_liquido": "Lucro Liquido",
        "roi_vs_lucro": "ROI vs Lucro Liquido",
        "composicao_comissao_cashback": "Composicao Comissao Cashback",
        "rentabilidade_por_comprador": "Rentabilidade por Comprador",
        "guardrails_escala": "Guardrails de Escala",
    }
    return titulos.get(nome, nome.replace("_", " ").title())


def montar_apendice_auditoria(json_auditavel, resposta_llm):
    blocos = resposta_llm.get("blocos_escolhidos", [])

    linhas = [
        "## Apendice de auditoria",
        "",
        "### Blocos escolhidos pela LLM",
    ]

    linhas.extend(f"- {bloco}" for bloco in blocos)

    linhas.append("")
    linhas.append("### Rankings dos KPIs de decisao")

    for metrica, titulo in metricas_decisao():
        linhas.extend(montar_ranking_metrica(json_auditavel, metrica, titulo))

    return "\n".join(linhas)


def metricas_decisao():
    return [
        ("lucro_liquido", "Lucro liquido"),
        ("roi", "ROI"),
        ("lucro_por_comprador", "Lucro por comprador"),
        ("gmv", "GMV"),
        ("total_compradores", "Compradores totais"),
    ]


def montar_ranking_metrica(json_auditavel, metrica, titulo):
    ranking = sorted(
        json_auditavel["kpis_por_grupo"].items(),
        key=lambda item: valor_ordenacao(item[1].get(metrica)),
        reverse=True,
    )

    linhas = [
        "",
        f"#### Ranking por {titulo}",
        "",
        "| Posicao | Grupo | Valor | Elegivel |",
        "| --- | --- | --- | --- |",
    ]

    for indice, (grupo, kpis) in enumerate(ranking, start=1):
        guardrail = json_auditavel["guardrails"][grupo]
        linhas.append(
            "| "
            + " | ".join([
                str(indice),
                grupo,
                formatar_kpi(metrica, kpis.get(metrica)),
                "sim" if guardrail["elegivel"] else "nao",
            ])
            + " |"
        )

    return linhas


def valor_ordenacao(valor):
    if valor is None:
        return float("-inf")

    return valor


def formatar_kpi(metrica, valor):
    if metrica in {
        "lucro_liquido",
        "lucro_por_comprador",
        "gmv",
    }:
        return formatar_moeda(valor)

    if metrica == "roi":
        return formatar_roi(valor)

    if metrica == "total_compradores":
        return formatar_inteiro(valor)

    return str(valor)


def formatar_moeda(valor):
    if valor is None:
        return "indisponivel"

    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_roi(valor):
    if valor is None:
        return "indisponivel"

    return f"{valor:.2f}x".replace(".", ",")


def formatar_percentual(valor):
    if valor is None:
        return "indisponivel"

    return f"{valor * 100:.1f}%".replace(".", ",")


def formatar_inteiro(valor):
    if valor is None:
        return "indisponivel"

    return f"{int(round(valor)):,.0f}".replace(",", ".")

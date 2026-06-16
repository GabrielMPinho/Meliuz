def gerar_graficos(json_auditavel, output_dir):
    import os

    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    os.makedirs(output_dir, exist_ok=True)

    arquivos = []
    avisos = []

    COR_VENCEDOR = "#007F7A"
    COR_NEUTRA = "#9CA3AF"
    COR_INELEGIVEL = "#D1D5DB"
    COR_LUCRO = "#007F7A"
    COR_ROI = "#374151"
    COR_COMISSAO = "#2A9D8F"
    COR_CASHBACK = "#E76F51"
    COR_ALERTA = "#F4A261"
    COR_CRITICO = "#D62828"

    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })

    def caminho_arquivo(nome_arquivo):
        return os.path.join(output_dir, nome_arquivo)

    def salvar(fig, nome_arquivo):
        caminho = caminho_arquivo(nome_arquivo)
        fig.savefig(caminho, dpi=150, bbox_inches="tight")
        plt.close(fig)
        arquivos.append(caminho)

    def limpar_eixos(ax):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(False)

    def formatar_reais(valor, _posicao):
        return f"R$ {valor:,.0f}".replace(",", ".")

    def formatar_percentual(valor, _posicao):
        return f"{valor:.0%}"

    def formatar_roi(valor, _posicao):
        return f"{valor:.1f}x"

    def formatar_percentual_texto(valor):
        return f"{valor:.1%}".replace(".", ",")

    def adicionar_rotulos_horizontais(ax, barras, valores):
        limite_x = ax.get_xlim()[1]

        for barra, valor in zip(barras, valores):
            largura = barra.get_width()
            x = min(largura + limite_x * 0.015, limite_x * 0.98)
            ax.text(
                x,
                barra.get_y() + barra.get_height() / 2,
                formatar_percentual_texto(valor),
                va="center",
                ha="left",
                fontsize=9,
                color="#111827",
            )

    def cor_grupo(grupo):
        if not json_auditavel["guardrails"][grupo]["elegivel"]:
            return COR_INELEGIVEL

        if grupo == json_auditavel["decisao"].get("vencedor"):
            return COR_VENCEDOR

        return COR_NEUTRA

    def grupos_validos(metricas, nome_grafico):
        grupos = []

        for grupo, kpis in json_auditavel["kpis_por_grupo"].items():
            metricas_none = [
                metrica for metrica in metricas
                if kpis.get(metrica) is None
            ]

            if metricas_none:
                avisos.append(
                    f"{grupo} ignorado em {nome_grafico} por valor None em: "
                    + ", ".join(metricas_none)
                    + "."
                )
                continue

            grupos.append(grupo)

        return grupos

    def largura_figura_vertical(grupos):
        return max(8.5, len(grupos) * 1.15 + 2)

    def altura_figura_horizontal(grupos):
        return max(4.8, len(grupos) * 0.55 + 2)

    def ajustar_rotulos_x(ax, grupos):
        if len(grupos) > 8:
            ax.tick_params(axis="x", labelrotation=45)
            for label in ax.get_xticklabels():
                label.set_ha("right")
        elif len(grupos) > 4:
            ax.tick_params(axis="x", labelrotation=30)
            for label in ax.get_xticklabels():
                label.set_ha("right")

    def figura_sem_dados(titulo, nome_arquivo):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.set_title(titulo)
        ax.text(
            0.5,
            0.5,
            "Sem dados disponiveis",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color=COR_NEUTRA,
        )
        ax.set_axis_off()
        salvar(fig, nome_arquivo)

    def grafico_lucro_liquido():
        titulo = "Lucro Líquido por Grupo"
        nome_arquivo = "lucro_liquido.png"
        grupos = grupos_validos(["lucro_liquido"], nome_arquivo)

        if not grupos:
            avisos.append(f"Nenhum grupo valido para {nome_arquivo}.")
            figura_sem_dados(titulo, nome_arquivo)
            return

        valores = [
            json_auditavel["kpis_por_grupo"][grupo]["lucro_liquido"]
            for grupo in grupos
        ]

        fig, ax = plt.subplots(figsize=(largura_figura_vertical(grupos), 4.8))
        ax.bar(grupos, valores, color=[cor_grupo(grupo) for grupo in grupos])
        ax.set_title(titulo)
        ax.set_ylabel("Lucro líquido")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_reais))
        ajustar_rotulos_x(ax, grupos)
        limpar_eixos(ax)
        salvar(fig, nome_arquivo)

    def grafico_roi_vs_lucro():
        titulo = "ROI vs Lucro Líquido por Grupo"
        nome_arquivo = "roi_vs_lucro.png"
        grupos = grupos_validos(["roi", "lucro_liquido"], nome_arquivo)

        if not grupos:
            avisos.append(f"Nenhum grupo valido para {nome_arquivo}.")
            figura_sem_dados(titulo, nome_arquivo)
            return

        posicoes = list(range(len(grupos)))
        largura = 0.36
        posicoes_lucro = [posicao - largura / 2 for posicao in posicoes]
        posicoes_roi = [posicao + largura / 2 for posicao in posicoes]

        lucro = [
            json_auditavel["kpis_por_grupo"][grupo]["lucro_liquido"]
            for grupo in grupos
        ]
        roi = [
            json_auditavel["kpis_por_grupo"][grupo]["roi"]
            for grupo in grupos
        ]
        alphas = [
            0.35 if not json_auditavel["guardrails"][grupo]["elegivel"] else 1
            for grupo in grupos
        ]

        fig, ax_lucro = plt.subplots(
            figsize=(largura_figura_vertical(grupos), 4.8)
        )
        ax_roi = ax_lucro.twinx()

        barras_lucro = ax_lucro.bar(
            posicoes_lucro,
            lucro,
            width=largura,
            color=COR_LUCRO,
            label="Lucro líquido",
        )
        barras_roi = ax_roi.bar(
            posicoes_roi,
            roi,
            width=largura,
            color=COR_ROI,
            label="ROI",
        )

        for barra, alpha in zip(barras_lucro, alphas):
            barra.set_alpha(alpha)

        for barra, alpha in zip(barras_roi, alphas):
            barra.set_alpha(alpha)

        ax_lucro.set_title(titulo)
        ax_lucro.set_xticks(posicoes)
        ax_lucro.set_xticklabels(grupos)
        ax_lucro.set_ylabel("Lucro líquido")
        ax_roi.set_ylabel("ROI")
        ax_lucro.set_ylim(0, max(lucro) * 1.15)
        ax_roi.set_ylim(0, max(roi) * 1.15)
        ax_lucro.yaxis.set_major_formatter(
            ticker.FuncFormatter(formatar_reais)
        )
        ax_roi.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_roi))
        ax_lucro.legend(
            [barras_lucro, barras_roi],
            ["Lucro liquido", "ROI"],
            loc="upper center",
            bbox_to_anchor=(0.5, 0.98),
            ncol=2,
            frameon=False,
        )
        ajustar_rotulos_x(ax_lucro, grupos)
        limpar_eixos(ax_lucro)
        ax_roi.grid(False)
        ax_roi.spines["top"].set_visible(False)
        salvar(fig, nome_arquivo)

    def grafico_composicao_comissao_cashback():
        titulo = "Composição: Comissão e Cashback por Grupo"
        nome_arquivo = "composicao_comissao_cashback.png"
        grupos = grupos_validos(
            ["comissao_total", "cashback_total"],
            nome_arquivo,
        )

        if not grupos:
            avisos.append(f"Nenhum grupo valido para {nome_arquivo}.")
            figura_sem_dados(titulo, nome_arquivo)
            return

        comissao = [
            json_auditavel["kpis_por_grupo"][grupo]["comissao_total"]
            for grupo in grupos
        ]
        cashback = [
            -json_auditavel["kpis_por_grupo"][grupo]["cashback_total"]
            for grupo in grupos
        ]
        alphas = [
            0.35 if not json_auditavel["guardrails"][grupo]["elegivel"] else 1
            for grupo in grupos
        ]

        fig, ax = plt.subplots(figsize=(largura_figura_vertical(grupos), 4.8))
        barras_comissao = ax.bar(
            grupos, comissao, color=COR_COMISSAO, label="Comissão total"
        )
        barras_cashback = ax.bar(
            grupos, cashback, color=COR_CASHBACK, label="Cashback total"
        )

        for barra, alpha in zip(barras_comissao, alphas):
            barra.set_alpha(alpha)

        for barra, alpha in zip(barras_cashback, alphas):
            barra.set_alpha(alpha)

        ax.axhline(0, color="#111827", linewidth=0.8)
        ax.set_title(titulo)
        ax.set_ylabel("Valor")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_reais))
        ax.legend(frameon=False)
        ajustar_rotulos_x(ax, grupos)
        limpar_eixos(ax)
        salvar(fig, nome_arquivo)

    def grafico_rentabilidade_por_comprador():
        titulo = "Rentabilidade por Comprador"
        nome_arquivo = "rentabilidade_por_comprador.png"
        grupos = grupos_validos(
            [
                "comissao_por_comprador",
                "cashback_por_comprador",
                "lucro_por_comprador",
            ],
            nome_arquivo,
        )

        if not grupos:
            avisos.append(f"Nenhum grupo valido para {nome_arquivo}.")
            figura_sem_dados(titulo, nome_arquivo)
            return

        posicoes = list(range(len(grupos)))
        largura = 0.26
        metricas = [
            ("comissao_por_comprador", "Comissão", COR_COMISSAO, -largura),
            ("cashback_por_comprador", "Cashback", COR_CASHBACK, 0),
            ("lucro_por_comprador", "Lucro", COR_LUCRO, largura),
        ]
        alphas = [
            0.35 if not json_auditavel["guardrails"][grupo]["elegivel"] else 1
            for grupo in grupos
        ]

        fig, ax = plt.subplots(figsize=(largura_figura_vertical(grupos), 4.8))

        for metrica, label, cor, deslocamento in metricas:
            valores = [
                json_auditavel["kpis_por_grupo"][grupo][metrica]
                for grupo in grupos
            ]
            barras = ax.bar(
                [posicao + deslocamento for posicao in posicoes],
                valores,
                width=largura,
                color=cor,
                label=label,
            )

            for barra, alpha in zip(barras, alphas):
                barra.set_alpha(alpha)

        ax.set_title(titulo)
        ax.set_xticks(posicoes)
        ax.set_xticklabels(grupos)
        ax.set_ylabel("Valor por comprador")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatar_reais))
        ax.legend(frameon=False)
        ajustar_rotulos_x(ax, grupos)
        limpar_eixos(ax)
        salvar(fig, nome_arquivo)

    def grafico_guardrails_escala():
        titulo = (
            "Guardrails de Escala: Perda vs Maior Grupo\n"
            "0% = grupo com maior GMV e compradores"
        )
        nome_arquivo = "guardrails_escala.png"
        grupos = grupos_validos(
            [
                "perda_gmv_maior_grupo",
                "perda_compradores_maior_grupo",
            ],
            nome_arquivo,
        )

        if not grupos:
            avisos.append(f"Nenhum grupo valido para {nome_arquivo}.")
            figura_sem_dados(titulo, nome_arquivo)
            return

        posicoes = list(range(len(grupos)))
        altura = 0.34
        perda_gmv = [
            json_auditavel["kpis_por_grupo"][grupo]["perda_gmv_maior_grupo"]
            for grupo in grupos
        ]
        perda_compradores = [
            json_auditavel["kpis_por_grupo"][grupo][
                "perda_compradores_maior_grupo"
            ]
            for grupo in grupos
        ]
        alphas = [
            0.35 if not json_auditavel["guardrails"][grupo]["elegivel"] else 1
            for grupo in grupos
        ]

        fig, ax = plt.subplots(figsize=(9.5, altura_figura_horizontal(grupos)))
        barras_gmv = ax.barh(
            [posicao - altura / 2 for posicao in posicoes],
            perda_gmv,
            height=altura,
            color=COR_LUCRO,
            label="Perda de GMV",
        )
        barras_compradores = ax.barh(
            [posicao + altura / 2 for posicao in posicoes],
            perda_compradores,
            height=altura,
            color=COR_ROI,
            label="Perda de compradores",
        )

        for barra, alpha in zip(barras_gmv, alphas):
            barra.set_alpha(alpha)

        for barra, alpha in zip(barras_compradores, alphas):
            barra.set_alpha(alpha)

        limite_x = min(
            1,
            max(0.45, max(perda_gmv + perda_compradores + [0.40]) * 1.15),
        )
        ax.set_xlim(0, limite_x)
        adicionar_rotulos_horizontais(ax, barras_gmv, perda_gmv)
        adicionar_rotulos_horizontais(
            ax,
            barras_compradores,
            perda_compradores,
        )

        ax.axvline(
            0.20,
            color=COR_ALERTA,
            linestyle="--",
            linewidth=1.4,
            label="Alerta: 20%",
        )
        ax.axvline(
            0.40,
            color=COR_CRITICO,
            linestyle="--",
            linewidth=1.4,
            label="Crítico: 40%",
        )
        ax.set_title(titulo)
        ax.set_yticks(posicoes)
        ax.set_yticklabels(grupos)
        ax.set_xlabel(
            "Perda percentual em relacao ao maior GMV/compradores"
        )
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(formatar_percentual))
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.01, 1),
            frameon=False,
        )
        fig.text(
            0.12,
            0.02,
            "Leitura: o grupo com 0% e o grupo com maior GMV e compradores "
            "do teste; o vencedor pode ter perda de escala se compensar em "
            "lucro e ROI.",
            fontsize=9,
            color="#4B5563",
        )
        fig.subplots_adjust(bottom=0.22)
        limpar_eixos(ax)
        salvar(fig, nome_arquivo)

    grafico_lucro_liquido()
    grafico_roi_vs_lucro()
    grafico_composicao_comissao_cashback()
    grafico_rentabilidade_por_comprador()
    grafico_guardrails_escala()

    return {
        "arquivos": arquivos,
        "avisos": avisos,
    }

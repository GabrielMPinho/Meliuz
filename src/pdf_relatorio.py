from datetime import date
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


MELIUZ_PINK = colors.HexColor("#F76BA4")
MELIUZ_DARK = colors.HexColor("#262132")
MELIUZ_TEXT = colors.HexColor("#334155")
MELIUZ_MUTED = colors.HexColor("#64748B")
MELIUZ_LIGHT = colors.HexColor("#FFF0F6")
MELIUZ_BORDER = colors.HexColor("#FBCFE8")
MELIUZ_TEAL = colors.HexColor("#008B7D")


def gerar_pdf_relatorio(
    json_auditavel,
    resposta_llm,
    graficos_resultado,
    caminho_saida,
    data_analise=None,
):
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    data_analise = data_analise or date.today()
    if isinstance(data_analise, str):
        data_analise_texto = data_analise
    else:
        data_analise_texto = data_analise.strftime("%d/%m/%Y")

    doc = SimpleDocTemplate(
        str(caminho_saida),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=2.1 * cm,
        bottomMargin=1.8 * cm,
        title=f"Relatorio A/B Cashback - {json_auditavel['metadados']['parceiro']}",
        author="Gabriel Manata de Pinho",
    )

    estilos = montar_estilos()
    story = []

    story.extend(montar_capa(json_auditavel, estilos))
    story.extend(montar_tabela_kpis_pdf(json_auditavel, estilos))
    story.extend(montar_metodologia_resumida(estilos))
    story.append(PageBreak())
    story.extend(montar_graficos_pdf(graficos_resultado, estilos))
    story.extend(montar_narrativa_pdf(resposta_llm, estilos))
    story.extend(montar_rankings_pdf(json_auditavel, estilos))

    doc.build(
        story,
        onFirstPage=lambda canvas, document: desenhar_marca_pagina(
            canvas,
            document,
            data_analise_texto,
        ),
        onLaterPages=lambda canvas, document: desenhar_marca_pagina(
            canvas,
            document,
            data_analise_texto,
        ),
    )

    return str(caminho_saida)


def montar_estilos():
    base = getSampleStyleSheet()
    estilos = {
        "title": ParagraphStyle(
            "MeliuzTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=MELIUZ_DARK,
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "MeliuzSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=MELIUZ_MUTED,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "MeliuzH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=MELIUZ_DARK,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "MeliuzH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=MELIUZ_DARK,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "MeliuzBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.1,
            leading=12.4,
            textColor=MELIUZ_TEXT,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "MeliuzSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=MELIUZ_MUTED,
            spaceAfter=4,
        ),
        "center": ParagraphStyle(
            "MeliuzCenter",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=MELIUZ_PINK,
            alignment=TA_CENTER,
        ),
        "bullet": ParagraphStyle(
            "MeliuzBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            leftIndent=10,
            firstLineIndent=-6,
            textColor=MELIUZ_TEXT,
            spaceAfter=4,
        ),
        "section": ParagraphStyle(
            "MeliuzSection",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=13.5,
            leading=16,
            textColor=MELIUZ_DARK,
            alignment=TA_LEFT,
        ),
        "section_subtitle": ParagraphStyle(
            "MeliuzSectionSubtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.4,
            leading=10.4,
            textColor=MELIUZ_MUTED,
            alignment=TA_LEFT,
        ),
        "metric_label": ParagraphStyle(
            "MeliuzMetricLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9,
            textColor=MELIUZ_MUTED,
        ),
        "metric_value": ParagraphStyle(
            "MeliuzMetricValue",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=12.2,
            leading=14,
            textColor=MELIUZ_DARK,
        ),
        "card_title": ParagraphStyle(
            "MeliuzCardTitle",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.2,
            leading=12.2,
            textColor=MELIUZ_DARK,
            spaceAfter=5,
        ),
        "card_body": ParagraphStyle(
            "MeliuzCardBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12,
            textColor=MELIUZ_TEXT,
            spaceAfter=5,
        ),
    }
    return estilos


def desenhar_marca_pagina(canvas, document, data_analise_texto):
    largura, altura = A4
    canvas.saveState()

    canvas.setFillColor(MELIUZ_LIGHT)
    canvas.roundRect(1.2 * cm, altura - 1.55 * cm, 2.8 * cm, 0.72 * cm, 10, fill=1, stroke=0)
    canvas.setFillColor(MELIUZ_PINK)
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(1.48 * cm, altura - 1.32 * cm, "Méliuz")

    canvas.setStrokeColor(MELIUZ_BORDER)
    canvas.setLineWidth(0.7)
    canvas.line(1.2 * cm, altura - 1.75 * cm, largura - 1.2 * cm, altura - 1.75 * cm)

    canvas.setStrokeColor(MELIUZ_BORDER)
    canvas.line(1.2 * cm, 1.15 * cm, largura - 1.2 * cm, 1.15 * cm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#8A7180"))
    assinatura = (
        f"Gabriel Manata de Pinho · Analise em {data_analise_texto} · "
        f"Pagina {document.page}"
    )
    canvas.drawRightString(largura - 1.2 * cm, 0.75 * cm, assinatura)

    canvas.restoreState()


def montar_capa(json_auditavel, estilos):
    metadados = json_auditavel["metadados"]
    decisao = json_auditavel["decisao"]

    story = [
        Spacer(1, 0.15 * cm),
        Paragraph(f"Relatorio A/B Cashback - {metadados['parceiro']}", estilos["title"]),
        Paragraph(
            (
                f"Periodo analisado: {metadados['periodo_inicio']} a "
                f"{metadados['periodo_fim']} · {metadados['total_dias']} dias · "
                f"{len(metadados['grupos'])} grupos"
            ),
            estilos["subtitle"],
        ),
        montar_metricas_chave(json_auditavel, estilos),
        Spacer(1, 0.18 * cm),
        montar_secao_pdf(
            "Resumo da decisao",
            "A decisao abaixo foi calculada pelo Python; a LLM apenas escreveu a narrativa.",
            estilos,
        ),
        montar_card_decisao(decisao, estilos),
        Spacer(1, 0.18 * cm),
        Paragraph(
            "Relatorio gerado por pipeline deterministico em Python, com narrativa "
            "validada por LLM e decisao final calculada fora da LLM.",
            estilos["body"],
        ),
    ]
    return story


def montar_metricas_chave(json_auditavel, estilos):
    decisao = json_auditavel["decisao"]
    vencedor = decisao.get("vencedor")

    if vencedor:
        kpis = json_auditavel["kpis_por_grupo"][vencedor]
        itens = [
            ("Vencedor", vencedor),
            ("Lucro liquido", formatar_moeda(kpis.get("lucro_liquido"))),
            ("ROI", formatar_roi(kpis.get("roi"))),
            ("Lucro/comprador", formatar_moeda(kpis.get("lucro_por_comprador"))),
        ]
    else:
        itens = [
            ("Vencedor", "Sem vencedor"),
            ("Status", str(decisao.get("status"))),
            ("Motivo", str(decisao.get("motivo"))),
            ("Recomendacao", "Nao escalar"),
        ]

    dados = [[
        [
            Paragraph(rotulo, estilos["metric_label"]),
            Paragraph(valor, estilos["metric_value"]),
        ]
        for rotulo, valor in itens
    ]]

    tabela = Table(dados, colWidths=[4.0 * cm, 4.1 * cm, 3.0 * cm, 4.5 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7FB")),
        ("BOX", (0, 0), (-1, -1), 0.7, MELIUZ_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, MELIUZ_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return tabela


def montar_secao_pdf(titulo, subtitulo, estilos):
    dados = [[Paragraph(titulo, estilos["section"])]]
    if subtitulo:
        dados.append([Paragraph(subtitulo, estilos["section_subtitle"])])

    tabela = Table(dados, colWidths=[16.4 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MELIUZ_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.7, MELIUZ_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 4, MELIUZ_PINK),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([Spacer(1, 0.12 * cm), tabela, Spacer(1, 0.18 * cm)])


def montar_card_decisao(decisao, estilos):
    vencedor = decisao.get("vencedor") or "sem vencedor"
    dados = [
        [
            Paragraph("<b>Vencedor</b>", estilos["small"]),
            Paragraph("<b>Motivo</b>", estilos["small"]),
            Paragraph("<b>Recomendacao</b>", estilos["small"]),
        ],
        [
            Paragraph(vencedor, estilos["body"]),
            Paragraph(str(decisao.get("motivo")), estilos["body"]),
            Paragraph(str(decisao.get("recomendacao")), estilos["body"]),
        ],
    ]

    tabela = Table(dados, colWidths=[3.0 * cm, 3.2 * cm, 9.2 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MELIUZ_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), MELIUZ_DARK),
        ("BOX", (0, 0), (-1, -1), 0.8, MELIUZ_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, MELIUZ_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return tabela


def montar_decisao_pdf(json_auditavel, estilos):
    decisao = json_auditavel["decisao"]
    story = [
        Paragraph("Decisao Calculada", estilos["h1"]),
        montar_card_decisao(decisao, estilos),
    ]

    alertas = decisao.get("alertas", [])
    if alertas:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("Alertas", estilos["h2"]))
        for alerta in alertas:
            story.append(Paragraph(f"• {texto_markdown(alerta)}", estilos["bullet"]))

    return story


def montar_tabela_kpis_pdf(json_auditavel, estilos):
    story = [
        montar_secao_pdf(
            "KPIs principais",
            "Indicadores usados para explicar a decisao e seus guardrails.",
            estilos,
        )
    ]
    headers = [
        "Grupo",
        "Elegivel",
        "Lucro",
        "ROI",
        "Lucro/Compr.",
        "GMV",
        "Compr.",
        "Margem GMV",
    ]
    dados = [[Paragraph(f"<b>{header}</b>", estilos["small"]) for header in headers]]

    for grupo, kpis in json_auditavel["kpis_por_grupo"].items():
        guardrail = json_auditavel["guardrails"][grupo]
        dados.append([
            Paragraph(grupo, estilos["small"]),
            Paragraph("sim" if guardrail["elegivel"] else "nao", estilos["small"]),
            Paragraph(formatar_moeda(kpis.get("lucro_liquido")), estilos["small"]),
            Paragraph(formatar_roi(kpis.get("roi")), estilos["small"]),
            Paragraph(formatar_moeda(kpis.get("lucro_por_comprador")), estilos["small"]),
            Paragraph(formatar_moeda(kpis.get("gmv")), estilos["small"]),
            Paragraph(formatar_inteiro(kpis.get("total_compradores")), estilos["small"]),
            Paragraph(formatar_percentual(kpis.get("margem_liquida_gmv")), estilos["small"]),
        ])

    tabela = Table(
        dados,
        colWidths=[
            2.1 * cm,
            1.7 * cm,
            2.5 * cm,
            1.3 * cm,
            2.4 * cm,
            2.8 * cm,
            2.0 * cm,
            2.0 * cm,
        ],
        repeatRows=1,
    )
    tabela.setStyle(estilo_tabela())
    story.append(tabela)
    return story


def montar_metodologia_resumida(estilos):
    dados = [
        [
            Paragraph("<b>Critério principal</b><br/>Maior lucro líquido total.", estilos["small"]),
            Paragraph("<b>Eficiência</b><br/>ROI e lucro por comprador validam a qualidade do resultado.", estilos["small"]),
        ],
        [
            Paragraph("<b>Escala</b><br/>GMV e compradores entram como guardrails, não como lucro.", estilos["small"]),
            Paragraph("<b>LLM</b><br/>A LLM interpreta os dados, mas não calcula nem troca o vencedor.", estilos["small"]),
        ],
    ]

    tabela = Table(dados, colWidths=[8.0 * cm, 8.0 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF7FB")),
        ("BOX", (0, 0), (-1, -1), 0.6, MELIUZ_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, MELIUZ_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [
        montar_secao_pdf(
            "Como ler a decisao",
            "Resumo operacional da regra aplicada antes da narrativa.",
            estilos,
        ),
        tabela,
    ]


def montar_graficos_pdf(graficos_resultado, estilos):
    arquivos = graficos_resultado.get("arquivos", []) if graficos_resultado else []
    story = [
        montar_secao_pdf(
            "Graficos",
            "Leitura visual dos principais sinais financeiros, unitarios e de escala.",
            estilos,
        )
    ]

    if not arquivos:
        story.append(Paragraph("Nenhum grafico foi gerado.", estilos["body"]))
        return story

    for indice, arquivo in enumerate(arquivos):
        caminho = Path(arquivo)
        if not caminho.exists():
            continue

        titulo = caminho.stem.replace("_", " ").title()
        guardrails = caminho.stem == "guardrails_escala"
        largura = 16.5 * cm if guardrails else 15.6 * cm
        altura = 10.2 * cm if guardrails else 7.1 * cm
        bloco = montar_card_grafico(titulo, caminho, largura, altura, estilos)
        story.append(KeepTogether(bloco))
        if indice in {1, 3}:
            story.append(PageBreak())

    return story


def montar_card_grafico(titulo, caminho, largura, altura, estilos):
    dados = [
        [Paragraph(titulo, estilos["card_title"])],
        [Image(str(caminho), width=largura, height=altura, kind="proportional")],
    ]
    tabela = Table(dados, colWidths=[16.5 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#FDE2EF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [tabela, Spacer(1, 0.22 * cm)]


def montar_narrativa_pdf(resposta_llm, estilos):
    story = [
        montar_secao_pdf(
            "Narrativa analitica",
            "Interpretacao executiva gerada pela LLM com base apenas no JSON auditavel.",
            estilos,
        )
    ]
    narrativa = resposta_llm.get("narrativa_markdown", "")
    story.extend(narrativa_para_cards(narrativa, estilos))
    return story


def montar_rankings_pdf(json_auditavel, estilos):
    story = [
        montar_secao_pdf(
            "Rankings dos KPIs de decisao",
            "Ordenacao completa dos indicadores que sustentam a decisao.",
            estilos,
        )
    ]

    cards = []
    for metrica, titulo in metricas_decisao():
        cards.append(montar_card_ranking(json_auditavel, metrica, titulo, estilos))

    linhas = []
    for indice in range(0, len(cards), 2):
        esquerda = cards[indice]
        direita = cards[indice + 1] if indice + 1 < len(cards) else ""
        linhas.append([esquerda, direita])

    grid = Table(linhas, colWidths=[8.15 * cm, 8.15 * cm])
    grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(grid)

    return story


def montar_card_ranking(json_auditavel, metrica, titulo, estilos):
    conteudo = [
        Paragraph(f"Ranking por {titulo}", estilos["card_title"]),
        montar_tabela_ranking(json_auditavel, metrica, estilos, compacto=True),
    ]

    card = Table([[conteudo]], colWidths=[7.75 * cm])
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#FDE2EF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return card


def montar_tabela_ranking(json_auditavel, metrica, estilos, compacto=False):
    ranking = sorted(
        json_auditavel["kpis_por_grupo"].items(),
        key=lambda item: item[1].get(metrica) if item[1].get(metrica) is not None else float("-inf"),
        reverse=True,
    )
    dados = [[
        Paragraph("<b>Pos.</b>", estilos["small"]),
        Paragraph("<b>Grupo</b>", estilos["small"]),
        Paragraph("<b>Valor</b>", estilos["small"]),
        Paragraph("<b>Elegivel</b>", estilos["small"]),
    ]]

    for posicao, (grupo, kpis) in enumerate(ranking, start=1):
        guardrail = json_auditavel["guardrails"][grupo]
        dados.append([
            Paragraph(str(posicao), estilos["small"]),
            Paragraph(grupo, estilos["small"]),
            Paragraph(formatar_kpi(metrica, kpis.get(metrica)), estilos["small"]),
            Paragraph("sim" if guardrail["elegivel"] else "nao", estilos["small"]),
        ])

    colunas = [0.8 * cm, 2.1 * cm, 2.7 * cm, 1.4 * cm] if compacto else [
        1.2 * cm,
        4.0 * cm,
        5.0 * cm,
        2.2 * cm,
    ]
    tabela = Table(dados, colWidths=colunas)
    tabela.setStyle(estilo_tabela(compacto=compacto))
    return tabela


def narrativa_para_cards(texto, estilos):
    secoes = extrair_secoes_narrativa(texto)
    flowables = []

    for indice, (titulo, paragrafos) in enumerate(secoes):
        destaque = indice == 0 or "sumario" in normalizar_ascii(titulo)
        flowables.append(montar_card_narrativa(titulo, paragrafos, estilos, destaque))
        flowables.append(Spacer(1, 0.18 * cm))

    return flowables


def extrair_secoes_narrativa(texto):
    secoes = []
    titulo_atual = "Leitura analitica"
    paragrafos = []
    buffer = []

    def flush_paragrafo():
        if buffer:
            paragrafo = " ".join(buffer).strip()
            if paragrafo:
                paragrafos.append(paragrafo)
            buffer.clear()

    def flush_secao():
        flush_paragrafo()
        if titulo_atual or paragrafos:
            secoes.append((titulo_atual, list(paragrafos)))
            paragrafos.clear()

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            flush_paragrafo()
            continue

        titulo = extrair_titulo_markdown(linha)
        if titulo:
            flush_secao()
            titulo_atual = titulo
            continue

        if linha.startswith("- "):
            flush_paragrafo()
            paragrafos.append("• " + linha[2:])
            continue

        buffer.append(linha)

    flush_secao()
    return [(titulo, paragrafos) for titulo, paragrafos in secoes if paragrafos]


def extrair_titulo_markdown(linha):
    if linha.startswith("## "):
        return linha[3:].strip()

    if linha.startswith("# "):
        return linha[2:].strip()

    match = re.fullmatch(r"\*\*(.+?)\*\*", linha)
    if match:
        return match.group(1).strip()

    return None


def montar_card_narrativa(titulo, paragrafos, estilos, destaque=False):
    conteudo = [Paragraph(texto_markdown(titulo), estilos["card_title"])]
    for paragrafo in paragrafos:
        estilo = estilos["card_body"]
        conteudo.append(Paragraph(texto_markdown(paragrafo), estilo))

    tabela = Table([[conteudo]], colWidths=[16.4 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MELIUZ_LIGHT if destaque else colors.white),
        ("BOX", (0, 0), (-1, -1), 0.7, MELIUZ_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 4, MELIUZ_PINK if destaque else MELIUZ_TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return KeepTogether([tabela])


def normalizar_ascii(texto):
    return (
        str(texto)
        .lower()
        .replace("á", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("õ", "o")
        .replace("ô", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )


def markdown_para_flowables(texto, estilos):
    flowables = []
    buffer = []

    def flush_buffer():
        if buffer:
            paragrafo = " ".join(buffer).strip()
            if paragrafo:
                flowables.append(Paragraph(texto_markdown(paragrafo), estilos["body"]))
            buffer.clear()

    for linha in texto.splitlines():
        linha = linha.strip()

        if not linha:
            flush_buffer()
            continue

        if linha.startswith("## "):
            flush_buffer()
            flowables.append(Paragraph(texto_markdown(linha[3:]), estilos["h2"]))
            continue

        if linha.startswith("# "):
            flush_buffer()
            flowables.append(Paragraph(texto_markdown(linha[2:]), estilos["h1"]))
            continue

        if linha.startswith("- "):
            flush_buffer()
            flowables.append(Paragraph("• " + texto_markdown(linha[2:]), estilos["bullet"]))
            continue

        buffer.append(linha)

    flush_buffer()
    return flowables


def texto_markdown(texto):
    texto = escape(str(texto))
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    return texto


def estilo_tabela(compacto=False):
    padding = 3 if compacto else 5
    fonte_grade = 0.3 if compacto else 0.35

    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MELIUZ_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, 0), MELIUZ_DARK),
        ("BOX", (0, 0), (-1, -1), 0.7, MELIUZ_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), fonte_grade, MELIUZ_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF7FB")]),
    ])


def metricas_decisao():
    return [
        ("lucro_liquido", "Lucro Liquido"),
        ("roi", "ROI"),
        ("lucro_por_comprador", "Lucro por Comprador"),
        ("gmv", "GMV"),
        ("total_compradores", "Compradores Totais"),
    ]


def formatar_kpi(metrica, valor):
    if metrica in {"lucro_liquido", "lucro_por_comprador", "gmv"}:
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

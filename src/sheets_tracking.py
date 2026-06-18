import csv
import logging
import os
import re
import shutil
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


COLUNAS_TRACKING_LEGADO = [
    "Nome do teste",
    "Parceiro",
    "Periodo",
    "Descricao",
    "Vencedor",
    "Resultado",
    "Decisao tomada",
    "Grupo maior lucro_liquido",
    "Valor maior lucro_liquido",
    "Grupo maior roi",
    "Valor maior roi",
    "Grupo maior lucro_por_comprador",
    "Valor maior lucro_por_comprador",
    "Grupo maior gmv",
    "Valor maior gmv",
    "Grupo maior total_compradores",
    "Valor maior total_compradores",
]

COLUNAS_TRACKING = [
    COLUNAS_TRACKING_LEGADO[0],
    "Teste realizado em",
    *COLUNAS_TRACKING_LEGADO[1:],
]

METRICAS_DECISAO = [
    ("lucro_liquido", "lucro_liquido"),
    ("roi", "roi"),
    ("lucro_por_comprador", "lucro_por_comprador"),
    ("gmv", "gmv"),
    ("total_compradores", "total_compradores"),
]


def atualizar_tracking_google_sheets(
    json_auditavel,
    sheet_url=None,
    output_dir="outputs",
    chrome_path=None,
    headless=True,
):
    carregar_env()

    sheet_url = resolver_sheet_url(sheet_url)
    chrome_path = chrome_path or os.getenv("MELIUZ_CHROME_PATH")

    linha = montar_linha_tracking(json_auditavel)
    linhas_existentes = ler_linhas_publicas(sheet_url)
    linhas_colar, linha_inicio, linhas_backup, regravar_tabela = preparar_append_tracking(
        linhas_existentes,
        [linha],
    )

    caminho_tsv = salvar_tsv_tracking(linhas_backup, output_dir)
    colar_linhas_no_google_sheets(
        linhas=linhas_colar,
        sheet_url=sheet_url,
        linha_inicio=linha_inicio,
        chrome_path=chrome_path,
        headless=headless,
    )

    validar_publicacao_append(
        sheet_url=sheet_url,
        linhas_esperadas=linhas_colar,
        quantidade_linhas_antes=0
        if regravar_tabela
        else contar_linhas_preenchidas(linhas_existentes),
    )

    return {
        "sheet_url": sheet_url,
        "linhas_adicionadas": 1,
        "linha_inicio": linha_inicio,
        "backup_tsv": str(caminho_tsv),
    }


def atualizar_tracking_varias_analises(
    analises,
    sheet_url=None,
    output_dir="outputs",
    chrome_path=None,
    headless=True,
):
    carregar_env()

    sheet_url = resolver_sheet_url(sheet_url)
    chrome_path = chrome_path or os.getenv("MELIUZ_CHROME_PATH")

    novas_linhas = []
    for analise in analises:
        novas_linhas.append(montar_linha_tracking(analise))

    linhas_existentes = ler_linhas_publicas(sheet_url)
    linhas_colar, linha_inicio, linhas_backup, regravar_tabela = preparar_append_tracking(
        linhas_existentes,
        novas_linhas,
    )

    caminho_tsv = salvar_tsv_tracking(linhas_backup, output_dir)
    colar_linhas_no_google_sheets(
        linhas=linhas_colar,
        sheet_url=sheet_url,
        linha_inicio=linha_inicio,
        chrome_path=chrome_path,
        headless=headless,
    )

    validar_publicacao_append(
        sheet_url=sheet_url,
        linhas_esperadas=linhas_colar,
        quantidade_linhas_antes=0
        if regravar_tabela
        else contar_linhas_preenchidas(linhas_existentes),
    )

    return {
        "sheet_url": sheet_url,
        "linhas_adicionadas": len(novas_linhas),
        "linha_inicio": linha_inicio,
        "backup_tsv": str(caminho_tsv),
    }


def montar_linha_tracking(json_auditavel):
    metadados = json_auditavel["metadados"]
    decisao = json_auditavel["decisao"]
    vencedor = decisao.get("vencedor") or "sem vencedor"
    motivo = decisao.get("motivo") or "sem motivo"

    linha = [
        f"Teste A/B Cashback - {metadados['parceiro']}",
        data_atual_br(),
        metadados["parceiro"],
        f"{metadados['periodo_inicio']} a {metadados['periodo_fim']}",
        (
            f"{len(metadados['grupos'])} grupos avaliados em "
            f"{metadados['total_dias']} dias."
        ),
        vencedor,
        f"{vencedor} venceu por {motivo}.",
        decisao.get("recomendacao") or "",
    ]

    for metrica, _titulo in METRICAS_DECISAO:
        grupo, valor = obter_vencedor_metrica(json_auditavel, metrica)
        linha.extend([grupo, formatar_kpi(metrica, valor)])

    return linha


def preparar_append_tracking(linhas_existentes, novas_linhas):
    linhas_existentes, schema_migrado = normalizar_schema_tracking(linhas_existentes)

    if not linhas_existentes:
        linhas_colar = [COLUNAS_TRACKING, *novas_linhas]
        return linhas_colar, 1, linhas_colar, True

    linha_inicio = len(linhas_existentes) + 1

    if linhas_existentes[0] == COLUNAS_TRACKING:
        if schema_migrado:
            linhas_colar = [*linhas_existentes, *novas_linhas]
            return linhas_colar, 1, linhas_colar, True

        linhas_colar = novas_linhas
        return linhas_colar, linha_inicio, [*linhas_existentes, *novas_linhas], False

    linhas_colar = [COLUNAS_TRACKING, *novas_linhas]
    return linhas_colar, linha_inicio, [*linhas_existentes, *linhas_colar], False


def obter_vencedor_metrica(json_auditavel, metrica):
    ranking = sorted(
        json_auditavel["kpis_por_grupo"].items(),
        key=lambda item: valor_ordenacao(item[1].get(metrica)),
        reverse=True,
    )

    if not ranking:
        return "", None

    grupo, kpis = ranking[0]
    return grupo, kpis.get(metrica)


def valor_ordenacao(valor):
    if valor is None:
        return float("-inf")

    return valor


def salvar_tsv_tracking(linhas, output_dir):
    caminho = Path(output_dir) / "google_sheets_resumo.tsv"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(linhas_para_tsv(linhas), encoding="utf-8")
    return caminho


def linhas_para_tsv(linhas):
    return "\n".join(
        "\t".join(normalizar_celula(celula) for celula in linha)
        for linha in linhas
    )


def normalizar_celula(valor):
    return str(valor).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def normalizar_tamanho_linha(linha, tamanho):
    linha = list(linha)
    if len(linha) < tamanho:
        linha.extend([""] * (tamanho - len(linha)))
    return linha[:tamanho]


def normalizar_linhas_preenchidas(linhas):
    linhas_normalizadas = []

    for linha in linhas:
        linha = normalizar_tamanho_linha(linha, len(COLUNAS_TRACKING))
        if any(celula for celula in linha):
            linhas_normalizadas.append(linha)

    return linhas_normalizadas


def normalizar_schema_tracking(linhas):
    linhas = [list(linha) for linha in linhas if any(celula for celula in linha)]

    if not linhas:
        return [], False

    cabecalho_atual = normalizar_tamanho_linha(
        linhas[0],
        len(COLUNAS_TRACKING),
    )
    if cabecalho_atual == COLUNAS_TRACKING:
        return normalizar_linhas_preenchidas(linhas), False

    cabecalho_legado = normalizar_tamanho_linha(
        linhas[0],
        len(COLUNAS_TRACKING_LEGADO),
    )
    if cabecalho_legado == COLUNAS_TRACKING_LEGADO:
        linhas_migradas = [COLUNAS_TRACKING]
        for linha in linhas[1:]:
            linha_legada = normalizar_tamanho_linha(
                linha,
                len(COLUNAS_TRACKING_LEGADO),
            )
            linhas_migradas.append([
                linha_legada[0],
                data_atual_br(),
                *linha_legada[1:],
            ])
        return linhas_migradas, True

    return normalizar_linhas_preenchidas(linhas), False


def contar_linhas_preenchidas(linhas):
    linhas_normalizadas, _schema_migrado = normalizar_schema_tracking(linhas)
    return len(linhas_normalizadas)


def migrar_tracking_google_sheets(
    sheet_url=None,
    output_dir="outputs",
    chrome_path=None,
    headless=True,
):
    carregar_env()

    sheet_url = resolver_sheet_url(sheet_url)
    chrome_path = chrome_path or os.getenv("MELIUZ_CHROME_PATH")

    linhas_existentes = ler_linhas_publicas(sheet_url)
    linhas_migradas, schema_migrado = normalizar_schema_tracking(linhas_existentes)

    if not linhas_migradas:
        linhas_migradas = [COLUNAS_TRACKING]
        schema_migrado = True

    caminho_tsv = salvar_tsv_tracking(linhas_migradas, output_dir)

    if schema_migrado:
        colar_linhas_no_google_sheets(
            linhas=linhas_migradas,
            sheet_url=sheet_url,
            linha_inicio=1,
            chrome_path=chrome_path,
            headless=headless,
        )
        validar_publicacao_append(
            sheet_url=sheet_url,
            linhas_esperadas=linhas_migradas,
            quantidade_linhas_antes=0,
        )

    return {
        "sheet_url": sheet_url,
        "schema_migrado": schema_migrado,
        "linhas": max(len(linhas_migradas) - 1, 0),
        "backup_tsv": str(caminho_tsv),
    }


def ler_linhas_publicas(sheet_url):
    url = montar_url_export_csv(sheet_url)

    ultimo_erro = None
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as resposta:
                conteudo = resposta.read().decode("utf-8-sig")
        except Exception as erro:
            ultimo_erro = erro
            time.sleep(2)
            continue

        if conteudo.strip():
            return list(csv.reader(conteudo.splitlines()))

        if tentativa < 2:
            time.sleep(2)

    if ultimo_erro:
        raise RuntimeError(
            "Nao foi possivel ler a exportacao publica do Google Sheets."
        ) from ultimo_erro

    return []


def colar_linhas_no_google_sheets(
    linhas,
    sheet_url,
    linha_inicio=1,
    chrome_path=None,
    headless=True,
):
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as erro:
        raise ModuleNotFoundError(
            "Pacote playwright nao instalado. Rode: pip install -r requirements.txt"
        ) from erro

    chrome_path = encontrar_chrome(chrome_path)
    tsv = linhas_para_tsv(linhas)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=chrome_path,
            headless=headless,
        )
        context = browser.new_context(
            locale="pt-BR",
            viewport={"width": 1440, "height": 900},
        )
        context.grant_permissions(
            ["clipboard-read", "clipboard-write"],
            origin="https://docs.google.com",
        )
        page = context.new_page()
        page.goto(sheet_url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(15000)

        texto_pagina = page.locator("body").inner_text(timeout=5000)
        if "Somente ver" in texto_pagina:
            browser.close()
            raise PermissionError(
                "A planilha abriu como Somente ver. "
                "Altere o compartilhamento para qualquer pessoa com o link editar."
            )

        selecionar_celula(page, linha_inicio)
        page.wait_for_timeout(500)
        page.evaluate("async text => await navigator.clipboard.writeText(text)", tsv)
        page.keyboard.press("Control+V")
        page.wait_for_timeout(12000)
        browser.close()


def selecionar_celula(page, linha_inicio):
    if linha_inicio <= 30:
        y_celula = 176 + ((linha_inicio - 1) * 21)
        page.mouse.click(96, y_celula)
        page.wait_for_timeout(500)
        return

    # Caixa de nome do Google Sheets, onde e possivel informar A1, A2 etc.
    page.mouse.click(24, 126)
    page.wait_for_timeout(200)
    page.keyboard.press("Control+A")
    page.keyboard.type(f"A{linha_inicio}")
    page.keyboard.press("Enter")
    page.wait_for_timeout(800)


def validar_publicacao_append(
    sheet_url,
    linhas_esperadas,
    quantidade_linhas_antes,
):
    linhas_esperadas = normalizar_linhas_preenchidas(linhas_esperadas)

    for _tentativa in range(15):
        linhas = normalizar_linhas_preenchidas(ler_linhas_publicas(sheet_url))
        if len(linhas) >= quantidade_linhas_antes + len(linhas_esperadas):
            novas_linhas = linhas[quantidade_linhas_antes:]
            if contem_sequencia(novas_linhas, linhas_esperadas):
                return True
        time.sleep(3)

    logger = logging.getLogger(__name__)
    logger.warning(
        "Dados foram colados na planilha, mas a exportacao publica ainda "
        "nao refletiu as alteracoes. O PDF foi gerado normalmente."
    )


def contem_sequencia(linhas, sequencia):
    tamanho = len(sequencia)
    if tamanho == 0:
        return True

    for inicio in range(0, len(linhas) - tamanho + 1):
        if linhas[inicio:inicio + tamanho] == sequencia:
            return True

    return False


def montar_url_export_csv(sheet_url):
    spreadsheet_id = extrair_spreadsheet_id(sheet_url)
    gid = extrair_gid(sheet_url)
    return (
        "https://docs.google.com/spreadsheets/d/"
        f"{spreadsheet_id}/export?format=csv&gid={gid}"
    )


def extrair_spreadsheet_id(sheet_url):
    match = re.search(r"/spreadsheets/d/([^/]+)", sheet_url)
    if not match:
        raise ValueError("URL de Google Sheets invalida.")
    return match.group(1)


def extrair_gid(sheet_url):
    parsed = urllib.parse.urlparse(sheet_url)
    query = urllib.parse.parse_qs(parsed.query)
    if "gid" in query:
        return query["gid"][0]

    fragment = urllib.parse.parse_qs(parsed.fragment)
    if "gid" in fragment:
        return fragment["gid"][0]

    return "0"


def encontrar_chrome(chrome_path=None):
    if chrome_path and Path(chrome_path).exists():
        return chrome_path

    candidatos = [
        os.getenv("CHROME_PATH"),
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("google-chrome"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]

    for candidato in candidatos:
        if candidato and Path(candidato).exists():
            return candidato

    raise FileNotFoundError(
        "Chrome ou Edge nao encontrado. Defina MELIUZ_CHROME_PATH no .env."
    )


def carregar_env(env_path=".env"):
    caminho = Path(env_path)
    if not caminho.exists():
        return

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()

        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")

        if chave and chave not in os.environ:
            os.environ[chave] = valor


def resolver_sheet_url(sheet_url=None):
    sheet_url = sheet_url or os.getenv("MELIUZ_SHEETS_URL")

    if not sheet_url:
        raise ValueError(
            "MELIUZ_SHEETS_URL nao encontrada. Defina a URL da planilha no "
            ".env ou passe --sheet-url."
        )

    return sheet_url


def formatar_kpi(metrica, valor):
    if metrica in {"lucro_liquido", "lucro_por_comprador", "gmv"}:
        return formatar_moeda(valor)

    if metrica == "roi":
        return formatar_roi(valor)

    if metrica == "total_compradores":
        return formatar_inteiro(valor)

    return str(valor)


def data_atual_br():
    return date.today().strftime("%d/%m/%Y")


def formatar_moeda(valor):
    if valor is None:
        return ""

    texto = f"R$ {valor:,.2f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_roi(valor):
    if valor is None:
        return ""

    return f"{valor:.2f}x".replace(".", ",")


def formatar_inteiro(valor):
    if valor is None:
        return ""

    return f"{int(round(valor)):,.0f}".replace(",", ".")

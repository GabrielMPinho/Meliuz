import argparse
import json
import re
import sys
from pathlib import Path

try:
    from limpeza import data_cleaning
    from json_auditavel import gerar_json_auditavel
    from graficos import gerar_graficos
    from llm_client import chamar_llm_openai
    from llm_relatorio import gerar_resposta_llm_simulada
    from pdf_relatorio import gerar_pdf_relatorio
    from relatorio import salvar_relatorio_markdown
    from sheets_tracking import atualizar_tracking_google_sheets
    from validacao_llm import validar_resposta_llm
except ModuleNotFoundError:
    from src.limpeza import data_cleaning
    from src.json_auditavel import gerar_json_auditavel
    from src.graficos import gerar_graficos
    from src.llm_client import chamar_llm_openai
    from src.llm_relatorio import gerar_resposta_llm_simulada
    from src.pdf_relatorio import gerar_pdf_relatorio
    from src.relatorio import salvar_relatorio_markdown
    from src.sheets_tracking import atualizar_tracking_google_sheets
    from src.validacao_llm import validar_resposta_llm


def executar_pipeline(
    caminho_csv,
    output_dir="outputs",
    llm="mock",
    model=None,
    update_sheets=False,
    sheet_url=None,
    chrome_path=None,
):
    caminho_csv = Path(caminho_csv)
    output_dir = Path(output_dir)

    df = data_cleaning(caminho_csv)
    json_auditavel = gerar_json_auditavel(df)

    parceiro_slug = slugificar(json_auditavel["metadados"]["parceiro"])
    diretorio_saida = output_dir / parceiro_slug
    diretorio_graficos = diretorio_saida / "graficos"
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    caminho_json = diretorio_saida / "analise.json"
    salvar_json(caminho_json, json_auditavel)

    graficos_resultado = gerar_graficos(json_auditavel, diretorio_graficos)

    resposta_llm = gerar_resposta_llm(
        llm=llm,
        json_auditavel=json_auditavel,
        model=model,
    )
    caminho_resposta = diretorio_saida / f"resposta_llm_{llm}.json"
    salvar_json(caminho_resposta, resposta_llm)

    validacao = validar_resposta_llm(json_auditavel, resposta_llm)
    caminho_validacao = diretorio_saida / "validacao_llm.json"
    salvar_json(caminho_validacao, validacao)

    if not validacao["valido"]:
        erros = "\n".join(validacao["erros"])
        raise ValueError(
            "Resposta da LLM nao passou na validacao:\n" + erros
        )

    caminho_relatorio = diretorio_saida / "relatorio.md"
    salvar_relatorio_markdown(
        json_auditavel=json_auditavel,
        resposta_llm=resposta_llm,
        graficos_resultado=graficos_resultado,
        caminho_saida=caminho_relatorio,
    )

    caminho_pdf = diretorio_saida / "relatorio.pdf"
    gerar_pdf_relatorio(
        json_auditavel=json_auditavel,
        resposta_llm=resposta_llm,
        graficos_resultado=graficos_resultado,
        caminho_saida=caminho_pdf,
    )

    resultado_sheets = None
    if update_sheets:
        resultado_sheets = atualizar_tracking_google_sheets(
            json_auditavel=json_auditavel,
            sheet_url=sheet_url,
            output_dir=output_dir,
            chrome_path=chrome_path,
        )

    return {
        "parceiro": json_auditavel["metadados"]["parceiro"],
        "diretorio_saida": str(diretorio_saida),
        "analise_json": str(caminho_json),
        "resposta_llm": str(caminho_resposta),
        "validacao_llm": str(caminho_validacao),
        "relatorio": str(caminho_relatorio),
        "pdf": str(caminho_pdf),
        "graficos": graficos_resultado["arquivos"],
        "avisos_graficos": graficos_resultado["avisos"],
        "google_sheets": resultado_sheets,
    }


def gerar_resposta_llm(llm, json_auditavel, model=None):
    if llm == "mock":
        return gerar_resposta_llm_simulada(json_auditavel)

    if llm == "openai":
        return chamar_llm_openai(json_auditavel, model=model)

    raise ValueError("LLM nao suportada. Use --llm mock ou --llm openai.")


def salvar_json(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(conteudo, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def slugificar(texto):
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = texto.strip("_")
    return texto or "analise"


def montar_parser():
    parser = argparse.ArgumentParser(
        description="Executa a analise A/B de cashback para um CSV."
    )
    parser.add_argument(
        "csv",
        help="Caminho do dataset CSV a ser analisado.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Diretorio base para salvar os artefatos.",
    )
    parser.add_argument(
        "--llm",
        default="mock",
        choices=["mock", "openai"],
        help="Fonte da narrativa LLM.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Modelo OpenAI para --llm openai. Se omitido, usa OPENAI_MODEL "
            "do .env."
        ),
    )
    parser.add_argument(
        "--update-sheets",
        action="store_true",
        help="Atualiza o tracking simples no Google Sheets ao final da analise.",
    )
    parser.add_argument(
        "--sheet-url",
        default=None,
        help=(
            "URL da planilha. Se omitido, usa MELIUZ_SHEETS_URL do .env."
        ),
    )
    parser.add_argument(
        "--chrome-path",
        default=None,
        help=(
            "Caminho do Chrome/Edge para atualizar Sheets. Se omitido, tenta "
            "MELIUZ_CHROME_PATH ou caminhos padrao do Windows."
        ),
    )
    return parser


def main():
    args = montar_parser().parse_args()
    try:
        resultado = executar_pipeline(
            caminho_csv=args.csv,
            output_dir=args.output_dir,
            llm=args.llm,
            model=args.model,
            update_sheets=args.update_sheets,
            sheet_url=args.sheet_url,
            chrome_path=args.chrome_path,
        )
    except Exception as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(resultado, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

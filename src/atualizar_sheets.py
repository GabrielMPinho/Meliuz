import argparse
import json
import sys
from pathlib import Path

try:
    from limpeza import data_cleaning
    from json_auditavel import gerar_json_auditavel
    from sheets_tracking import (
        atualizar_tracking_varias_analises,
        migrar_tracking_google_sheets,
    )
except ModuleNotFoundError:
    from src.limpeza import data_cleaning
    from src.json_auditavel import gerar_json_auditavel
    from src.sheets_tracking import (
        atualizar_tracking_varias_analises,
        migrar_tracking_google_sheets,
    )


def atualizar_sheets_csvs(
    caminhos_csv,
    sheet_url=None,
    output_dir="outputs",
    chrome_path=None,
    headless=True,
):
    analises = []

    for caminho_csv in caminhos_csv:
        df = data_cleaning(Path(caminho_csv))
        analises.append(gerar_json_auditavel(df))

    return atualizar_tracking_varias_analises(
        analises=analises,
        sheet_url=sheet_url,
        output_dir=output_dir,
        chrome_path=chrome_path,
        headless=headless,
    )


def montar_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Atualiza o tracking simples no Google Sheets com uma linha por "
            "CSV analisado."
        )
    )
    parser.add_argument(
        "csv",
        nargs="*",
        help="Caminhos dos datasets CSV a registrar no tracking.",
    )
    parser.add_argument(
        "--migrate-schema",
        action="store_true",
        help=(
            "Atualiza somente o cabecalho/schema da planilha, sem adicionar "
            "nova linha de teste."
        ),
    )
    parser.add_argument(
        "--sheet-url",
        default=None,
        help=(
            "URL da planilha. Se omitido, usa MELIUZ_SHEETS_URL do .env."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Diretorio para salvar o backup TSV enviado ao Sheets.",
    )
    parser.add_argument(
        "--chrome-path",
        default=None,
        help=(
            "Caminho do Chrome/Edge. Se omitido, tenta MELIUZ_CHROME_PATH "
            "ou os caminhos padrao do Windows."
        ),
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Abre o navegador visivel durante a atualizacao.",
    )
    return parser


def main():
    args = montar_parser().parse_args()
    try:
        if args.migrate_schema:
            resultado = migrar_tracking_google_sheets(
                sheet_url=args.sheet_url,
                output_dir=args.output_dir,
                chrome_path=args.chrome_path,
                headless=not args.no_headless,
            )
        else:
            if not args.csv:
                raise ValueError(
                    "Informe ao menos um CSV ou use --migrate-schema."
                )

            resultado = atualizar_sheets_csvs(
                caminhos_csv=args.csv,
                sheet_url=args.sheet_url,
                output_dir=args.output_dir,
                chrome_path=args.chrome_path,
                headless=not args.no_headless,
            )
    except Exception as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(resultado, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()

import json
import os
from pathlib import Path


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_MAX_OUTPUT_TOKENS = 5000


def chamar_llm_openai(
    json_auditavel,
    prompt_path="prompts/relatorio_llm.md",
    env_path=".env",
    model=None,
    max_output_tokens=None,
):
    RAIZ = Path(__file__).resolve().parent.parent
    prompt_path = str(RAIZ / prompt_path) if not Path(prompt_path).is_absolute() else prompt_path
    env_path = str(RAIZ / env_path) if not Path(env_path).is_absolute() else env_path

    carregar_env(env_path)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY nao encontrada. Preencha a chave no arquivo .env."
        )

    modelo = model or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
    limite_tokens = int(
        max_output_tokens
        or os.getenv("OPENAI_MAX_OUTPUT_TOKENS")
        or DEFAULT_MAX_OUTPUT_TOKENS
    )

    try:
        from openai import OpenAI
    except ModuleNotFoundError as erro:
        raise ModuleNotFoundError(
            "Pacote openai nao instalado. Rode: pip install -r requirements.txt"
        ) from erro

    prompt = montar_prompt(prompt_path, json_auditavel)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=modelo,
        input=prompt,
        max_output_tokens=limite_tokens,
        text={
            "format": {
                "type": "json_schema",
                "name": "relatorio_llm",
                "strict": True,
                "schema": schema_resposta_llm(),
            }
        },
    )

    texto_saida = extrair_texto_response(response)
    resposta = json.loads(texto_saida)

    return resposta


def montar_prompt(prompt_path, json_auditavel):
    caminho_prompt = Path(prompt_path)
    prompt = caminho_prompt.read_text(encoding="utf-8")
    dados = json.dumps(json_auditavel, ensure_ascii=False, indent=2)
    return prompt.replace("{json_auditavel}", dados)


def extrair_texto_response(response):
    texto = getattr(response, "output_text", None)
    if texto:
        return texto

    partes = []
    for item in getattr(response, "output", []) or []:
        for conteudo in getattr(item, "content", []) or []:
            texto_item = getattr(conteudo, "text", None)
            if texto_item:
                partes.append(texto_item)

    if partes:
        return "\n".join(partes)

    raise ValueError("A resposta da OpenAI nao retornou texto em output_text.")


def schema_resposta_llm():
    return {
        "type": "object",
        "properties": {
            "blocos_escolhidos": {
                "type": "array",
                "minItems": 2,
                "maxItems": 4,
                "items": {"type": "string"},
            },
            "narrativa_markdown": {
                "type": "string",
            },
        },
        "required": [
            "blocos_escolhidos",
            "narrativa_markdown",
        ],
        "additionalProperties": False,
    }


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

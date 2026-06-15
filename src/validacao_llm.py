def validar_resposta_llm(json_auditavel, resposta_llm):
    import json
    import unicodedata

    def normalizar_texto(texto):
        texto = str(texto).lower()
        texto = texto.replace("_", " ").replace("-", " ")
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(
            caractere
            for caractere in texto
            if not unicodedata.combining(caractere)
        )
        texto = "".join(
            caractere if caractere.isalnum() else " "
            for caractere in texto
        )
        return " ".join(texto.split())

    def contem(texto, trecho):
        return normalizar_texto(trecho) in normalizar_texto(texto)

    def carregar_resposta(resposta):
        if isinstance(resposta, dict):
            return resposta

        if isinstance(resposta, str):
            return json.loads(resposta)

        raise TypeError("A resposta da LLM deve ser dict ou string JSON.")

    def validar_formato(resposta, erros, avisos):
        chaves_obrigatorias = ["blocos_escolhidos", "narrativa_markdown"]

        for chave in chaves_obrigatorias:
            if chave not in resposta:
                erros.append(f"Campo obrigatorio ausente: {chave}.")

        chaves_extras = [
            chave for chave in resposta.keys()
            if chave not in chaves_obrigatorias
        ]

        if chaves_extras:
            avisos.append(
                "A resposta possui campos extras: "
                + ", ".join(chaves_extras)
                + "."
            )

    def validar_blocos(resposta, catalogo, erros):
        blocos = resposta.get("blocos_escolhidos")

        if not isinstance(blocos, list):
            erros.append("blocos_escolhidos deve ser uma lista.")
            return []

        if len(blocos) < 2 or len(blocos) > 4:
            erros.append("blocos_escolhidos deve conter entre 2 e 4 ids.")

        blocos_unicos = set()
        for bloco in blocos:
            if not isinstance(bloco, str):
                erros.append("Todos os blocos escolhidos devem ser strings.")
                continue

            if bloco in blocos_unicos:
                erros.append(f"Bloco duplicado em blocos_escolhidos: {bloco}.")

            blocos_unicos.add(bloco)

            if bloco not in catalogo:
                erros.append(f"Bloco inexistente no catalogo_blocos: {bloco}.")

        return blocos

    def validar_narrativa(resposta, catalogo, blocos, erros, avisos):
        narrativa = resposta.get("narrativa_markdown")

        if not isinstance(narrativa, str):
            erros.append("narrativa_markdown deve ser uma string.")
            return ""

        if not narrativa.strip():
            erros.append("narrativa_markdown nao pode estar vazia.")
            return narrativa

        for bloco in blocos:
            if bloco in catalogo:
                for kpi in catalogo[bloco]["kpis_envolvidos"]:
                    if not contem(narrativa, kpi):
                        avisos.append(
                            "A narrativa pode nao ter usado o KPI "
                            f"'{kpi}' do bloco '{bloco}'."
                        )

        return narrativa

    def validar_decisao(json_auditavel, narrativa, erros):
        decisao = json_auditavel["decisao"]
        vencedor = decisao.get("vencedor")
        recomendacao = decisao.get("recomendacao")

        if vencedor is None:
            if not contem(narrativa, "nao escalar"):
                erros.append(
                    "Sem vencedor, a narrativa deve deixar claro que nao "
                    "recomenda escalar nenhum grupo."
                )
            return

        if not contem(narrativa, vencedor):
            erros.append(
                f"A narrativa nao menciona o vencedor definido: {vencedor}."
            )

        if recomendacao and not contem(narrativa, recomendacao):
            erros.append(
                "A narrativa nao menciona a recomendacao calculada pela "
                "decisao_final."
            )

        outros_grupos = [
            grupo for grupo in json_auditavel["metadados"]["grupos"]
            if grupo != vencedor
        ]

        for grupo in outros_grupos:
            if contem(narrativa, f"escalar {grupo}"):
                erros.append(
                    "A narrativa sugere escalar um grupo diferente do "
                    f"vencedor: {grupo}."
                )

    def validar_alertas_obrigatorios(json_auditavel, narrativa, erros):
        decisao = json_auditavel["decisao"]

        if decisao.get("empate_tecnico") and not (
            contem(narrativa, "empate tecnico")
            or contem(narrativa, "diferenca pequena")
        ):
            erros.append(
                "A narrativa deve mencionar o empate tecnico ou a diferenca "
                "pequena entre os candidatos."
            )

        if decisao.get("motivo") == "unico_elegivel" and not (
            contem(narrativa, "unico elegivel")
            or contem(narrativa, "apenas um grupo")
            or contem(narrativa, "so um grupo")
        ):
            erros.append(
                "A narrativa deve mencionar que apenas um grupo foi elegivel."
            )

        for grupo, guardrail in json_auditavel["guardrails"].items():
            escala_gmv = guardrail["escala_gmv"]
            escala_compradores = guardrail["escala_compradores"]

            if escala_gmv in ["alerta", "critico"] or escala_compradores in [
                "alerta",
                "critico",
            ]:
                menciona_grupo = contem(narrativa, grupo)
                menciona_risco = (
                    contem(narrativa, "escala")
                    or contem(narrativa, "risco")
                    or contem(narrativa, "limitacao")
                    or contem(narrativa, "critico")
                    or contem(narrativa, "alerta")
                )

                if not menciona_grupo or not menciona_risco:
                    erros.append(
                        "A narrativa deve mencionar o guardrail de escala "
                        f"do grupo {grupo}."
                    )

    erros = []
    avisos = []

    try:
        resposta = carregar_resposta(resposta_llm)
    except (TypeError, json.JSONDecodeError) as erro:
        return {
            "valido": False,
            "erros": [f"Resposta da LLM nao e um JSON valido: {erro}"],
            "avisos": [],
            "resposta": None,
            "blocos_validados": [],
        }

    if not isinstance(resposta, dict):
        return {
            "valido": False,
            "erros": ["Resposta da LLM deve ser um objeto JSON."],
            "avisos": [],
            "resposta": resposta,
            "blocos_validados": [],
        }

    catalogo = json_auditavel["catalogo_blocos"]

    validar_formato(resposta, erros, avisos)
    blocos = validar_blocos(resposta, catalogo, erros)
    narrativa = validar_narrativa(
        resposta, catalogo, blocos, erros, avisos
    )

    if narrativa:
        validar_decisao(json_auditavel, narrativa, erros)
        validar_alertas_obrigatorios(json_auditavel, narrativa, erros)

    blocos_validados = [
        catalogo[bloco]
        for bloco in blocos
        if isinstance(bloco, str) and bloco in catalogo
    ]

    return {
        "valido": len(erros) == 0,
        "erros": erros,
        "avisos": avisos,
        "resposta": resposta,
        "blocos_validados": blocos_validados,
    }


def validar_escolha_llm(json_auditavel, resposta_llm):
    return validar_resposta_llm(json_auditavel, resposta_llm)

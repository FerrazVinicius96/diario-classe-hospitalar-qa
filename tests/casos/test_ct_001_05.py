from apoio import abrir_login, app_url, esperar_url, finalizar, texto_limpo


def _enviar(page, cpf: str, senha: str) -> str:
    abrir_login(page)
    page.evaluate("() => document.querySelectorAll('input').forEach(i => i.removeAttribute('required'))")
    page.fill("#login", cpf)
    page.fill("#password", senha)
    with page.expect_navigation():
        page.click("button[type=submit]")
    erros = page.locator(".dch-error, .text-danger").all_inner_texts()
    return " | ".join(texto_limpo(e) for e in erros if texto_limpo(e))


def test_ct_001_05(page, registro):
    erro_cpf = _enviar(page, "", "QA-qualquer-1")
    registro.passo(acao="enviar com CPF vazio", url_final=page.url, mensagens=erro_cpf)
    registro.evidencia(page, "cpf_vazio")
    registro.conferir(bool(erro_cpf) and "CPF" in erro_cpf, f"Sem mensagem de CPF obrigatório (obtido {erro_cpf!r})")

    erro_senha = _enviar(page, "903.000.005-88", "")
    registro.passo(acao="enviar com senha vazia", url_final=page.url, mensagens=erro_senha)
    registro.evidencia(page, "senha_vazia")
    registro.conferir(bool(erro_senha) and "Senha" in erro_senha, f"Sem mensagem de senha obrigatória (obtido {erro_senha!r})")

    registro.observar(f"Textos de obrigatoriedade exibidos: {erro_cpf!r} e {erro_senha!r}; "
                      "revisar a redação (o texto não traz o verbo, ex.: 'O campo Senha é obrigatório.').")

    page.goto(f"{app_url()}/dashboard")
    registro.conferir(esperar_url(page, r"/welcome"), "Sessão criada com campo em branco")
    finalizar(registro)

from apoio import RN_04_1_TEXTO, RN_04_1_TITULO, app_url, finalizar, texto_limpo


def test_ct_003_01(page, registro):
    resposta = page.goto(f"{app_url()}/welcome/acessoNegado")
    titulo = texto_limpo(page.locator("h1").inner_text())
    mensagem = texto_limpo(page.locator(".auth-text").inner_text())
    botao = texto_limpo(page.locator("a.dch-btn").inner_text())
    registro.passo(acao="abrir /welcome/acessoNegado", status_http=resposta.status if resposta else None,
                   url_final=page.url, titulo=titulo, mensagem=mensagem, botao=botao)
    registro.evidencia(page)
    registro.conferir(titulo == RN_04_1_TITULO, f"Título difere do RN-04.1: {titulo!r}")
    registro.conferir(mensagem == RN_04_1_TEXTO, f"Texto difere do RN-04.1: {mensagem!r}")
    registro.conferir(botao == "Sair com segurança", f"Botão {botao!r}")
    registro.observar("Confere só o texto; o fluxo pelo Conecta (CT-003-02) depende do client_secret.")
    finalizar(registro)
